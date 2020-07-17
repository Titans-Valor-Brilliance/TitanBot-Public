import requests
import json
import asyncio
import time
from src.utils.titan import titan
from src import TCACHE_PATH
from datetime import datetime

LTERURL = "https://api.wynncraft.com/public_api.php?action=territoryList"

def write_territories(dat):
    with open(TCACHE_PATH, 'r') as f:
        old = json.load(f)
    old["cache"] = dat
    with open(TCACHE_PATH, 'w') as f:
        json.dump(old, f)

def attack_gain_update():
    dat = requests.get(LTERURL).json()
    nowhours = time.strftime("%H:%M").split(":")
    if int(nowhours[0]) == 0 and 0 < int(nowhours[1]) < 10:
        for key in titan.ffas.keys():
            if key != "ffas":
                titan.ffas.update({key:{"latest":""}})
    else:
        for k, v in dat["territories"].items():
            now = datetime.utcnow().timestamp()
            if v["guild"] != titan.ffas[k]["latest"]:
                captured = datetime.strptime(v["acquired"], "%Y-%m-%d %H:%M:%S").timestamp()
                dt = now-captured
                titan.ffas[k].update({v["guild"]: titan.ffas[k].get(v["guild"],0)+dt})
                titan.ffas[k]["latest"] = v["guild"]
            else:
                titan.ffas[k].update({v["guild"]: titan.ffas[k].get(v["guild"],0)+titan.config["tercheck"]})
    titan.save_ffas()
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
            await chn.send(f"<@&683785435117256939> WE'RE UNDER HEAVY ATTACK. TERRITORIES LOST: {str(res)}")
        await asyncio.sleep(titan.config["tercheck"])