import requests
import json
import asyncio
import time
from src.utils.titan import titan
from src import TCACHE_PATH
from datetime import datetime

LTERURL = "https://api.wynncraft.com/public_api.php?action=territoryList"
LEADURL= "https://api.wynncraft.com/public_api.php?action=statsLeaderboard&type=guild&timeframe=alltime"

def write_territories(dat):
    with open(TCACHE_PATH, 'r') as f:
        old = json.load(f)
    old["cache"] = dat
    with open(TCACHE_PATH, 'w') as f:
        json.dump(old, f)

def attack_gain_update():
    dat = requests.get(LTERURL).json()
    nowhours = time.strftime("%H:%M").split(":")
    if int(nowhours[1]) < 5:
        # Also do leaderboard tracking
        leaderboard = requests.get(LEADURL).json()
        new_data = {}
        for guild in leaderboard["data"]:
            new_data.update({guild["name"]: guild["xp"]})
        titan.lead["last"].pop(0)
        titan.lead["last"].append(new_data)
        titan.save_lead()
    # UTC IS 4 HOURS AHEAD OF EST :I
    if int(nowhours[0]) == 4 and 0 < int(nowhours[1]) < 5:
        for key in titan.ffas.keys():
            if key != "ffas":
                titan.ffas.update({key:{"latest":""}})
    else:
        for k, v in dat["territories"].items():
            now = datetime.utcnow().timestamp()

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
        if res and time.time() > titan.warning_timeout:
            await chn.send(f"<@&683785435117256939> WE'RE UNDER HEAVY ATTACK. TERRITORIES LOST: {str(res)}")
        await asyncio.sleep(titan.config["tercheck"])