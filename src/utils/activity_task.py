import json
import requests
from src.utils.titan import titan
import asyncio
import aiohttp
import discord
import time
import reqcache
import re
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

async def get_members_activity(msg: discord.Message, members: list, limit) -> list: # the msg is needed to update progress bar
    total = len(members)
    sess = aiohttp.ClientSession()
    tasks = []
    for name, uuid in members[:limit]:
        tasks.append(asyncio.create_task(reqcache.aget(MEMBERURL.format(uuid), sess)))
    d = await asyncio.gather(*tasks)
    g = []
    i = 0
    while i < len(d):
        online = bool(re.search("online\":.+?,",d[i])[0][9:-1])
        if online:
            name = re.search("username\":.+?,",d[i])[0][11:-2]
            tstamp = datetime.timestamp(datetime.strptime(re.search("lastJoin\":.+?,",d[i])[0][11:-2], "%Y-%m-%dT%H:%M:%S.%fZ"))
            g.append((name, tstamp))
        i += 1
    await sess.close()
    return g

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
            chn = titan.client.get_channel(titan.config["genChn"])
            await chn.send("<- %s Left" % m)
    for m in marked_for_del:
        del old[m]
    with open(ACTIVE_PATH, 'w') as f:
        json.dump(old, f)

async def write_members():
    chn = titan.client.get_channel(titan.config["genChn"])
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