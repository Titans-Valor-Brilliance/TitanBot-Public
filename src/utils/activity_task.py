import json
import requests
from src.utils.titan import titan
import asyncio
import discord
import time
from src import ACTIVE_PATH

URL = "https://api-legacy.wynncraft.com/public_api.php?action=onlinePlayers"
GUILD = "https://api-legacy.wynncraft.com/public_api.php?action=guildStats&command=Titans%20Valor"

def get_members() -> set:
    data = requests.get(GUILD).json()
    return {m["name"] for m in data["members"]}


def get_online() -> set:
    data = requests.get(URL).json()
    return {member for _, memberlist in data.items() for member in memberlist}
    
def get_current_members():
    members = get_members()
    kick_players(members)
    return members & get_online()

def write_online():
    current = time.time()
    members = get_current_members()
    with open(ACTIVE_PATH, 'r') as f:
        old = json.load(f)
    for member in members:
        old.update({member:current})
    with open(ACTIVE_PATH, 'w') as f:
        json.dump(old, f)

def kick_players(memberlist):
    # remove them from the activity list
    with open(ACTIVE_PATH, 'r') as f:
        old = json.load(f)
    marked_for_del = []
    for m in old:
        if not m in memberlist:
            marked_for_del.append(m)
    for m in marked_for_del:
        del old[m]
    with open(ACTIVE_PATH, 'w') as f:
        json.dump(old, f)

async def write_online_task(client: discord.Client):
    await client.wait_until_ready()
    while not client.is_closed():
        write_online()
        await asyncio.sleep(titan.config["onlinecheck"])