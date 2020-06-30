import requests
import json
import asyncio
from src.utils.titan import titan
from src import TCACHE_PATH

LTERURL = "https://api.wynncraft.com/public_api.php?action=territoryList"

def write_territories(dat):
    with open(TCACHE_PATH, 'r') as f:
        old = json.load(f)
    old["cache"] = dat
    with open(TCACHE_PATH, 'w') as f:
        json.dump(old, f)

def attack_gain_update():
    dat = requests.get(LTERURL).json()
    lost = []
    with open(TCACHE_PATH, 'r') as f:
        old = json.load(f)
    c = 0
    for territory in titan.artemis["ANO"]:
        if not dat["territories"][territory]["guild"] in {"Titans Valor", "Seekers of Arx"}:
            lost.append(territory)
            c += 1
    if c >= 3 and old["lose"] == 0: # urgent
        old["lose"] = 1
        with open(TCACHE_PATH, 'w') as f:
            json.dump(old, f)
        return lost
    elif c < 3:
        old["lose"] = 0
    with open(TCACHE_PATH, 'w') as f:
            json.dump(old, f)
    return 0

async def check_territories_task(client):
    await client.wait_until_ready()
    chn = client.get_channel(titan.config["warChn"])
    while not client.is_closed():
        res = attack_gain_update()
        if res:
            await chn.send(f"<PING> WE'RE UNDER HEAVY ATTACK. TERRITORIES LOST: {str(res)}")
        await asyncio.sleep(titan.config["tercheck"])