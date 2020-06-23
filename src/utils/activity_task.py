import json
import requests
from src.utils.titan import titan
import asyncio
import discord
import time
from datetime import datetime
from src import ACTIVE_PATH

URL = "https://api-legacy.wynncraft.com/public_api.php?action=onlinePlayers"
GUILD = "https://api.wynncraft.com/public_api.php?action=guildStats&command=Titans%20Valor"
MEMBERURL = "https://api.wynncraft.com/v2/player/{}/stats"

def get_members() -> set:
    data = requests.get(GUILD).json()
    return {m["name"] for m in data["members"]}

def get_members_uuid() -> list: # gets both
    data = requests.get(GUILD).json()
    return [(m["name"], m["uuid"]) for m in data["members"]]

async def get_members_activity(msg: discord.Message, members: list) -> list: # the msg is needed to update progress bar
    d = []
    total = len(members)
    i = 0
    for name, uuid in members:
        req = requests.get(MEMBERURL.format(uuid)).json()
        if len(req["data"]) > 0 and not req["data"][0]["meta"]["location"]["online"]:
            tstamp = datetime.timestamp(datetime.strptime(req["data"][0]["meta"]["lastJoin"], "%Y-%m-%dT%H:%M:%S.%fZ"))
            d.append((name, tstamp))
        i += 1
        if i % 10 == 0:
            # print(i/total*20, '='*int(i/total*20)+'-'*int(20-i/total*20))
            await msg.edit(content='`'+'='*int(i/total*20)+'-'*int(20-i/total*20)+'`')
    return d

def get_online() -> set:
    data = requests.get(URL).json()
    return {member for _, memberlist in data.items() for member in memberlist}
    
async def get_current_members():
    members = get_members()
    await kick_players(members)
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

async def kick_players(memberlist):
    # remove them from the activity list
    with open(ACTIVE_PATH, 'r') as f:
        old = json.load(f)
    marked_for_del = []
    for m in old:
        if not m in memberlist:
            marked_for_del.append(m)
            chn = titan.client.get_channel(titan.config["appChn"])
            await chn.send("<- %s Left" % m)
    for m in marked_for_del:
        del old[m]
    with open(ACTIVE_PATH, 'w') as f:
        json.dump(old, f)

async def write_members():
    chn = titan.client.get_channel(titan.config["appChn"])
    with open(ACTIVE_PATH, 'r') as f:
        members = set(json.load(f))
    new = get_members()
    with open(ACTIVE_PATH, 'w') as f:
        json.dump(list(new), f)
    left = members - new
    for member in left:
        await chn.send("<- %s Left" % member)
    join = new - members
    for member in join:
        await chn.send("-> %s Joined" % member)

async def write_members_task(client: discord.Client):
    await client.wait_until_ready()
    new = get_members()
    with open(ACTIVE_PATH, 'w') as f:
        json.dump(list(new), f)
    while not client.is_closed():
        await write_members()
        await asyncio.sleep(titan.config["onlinecheck"])