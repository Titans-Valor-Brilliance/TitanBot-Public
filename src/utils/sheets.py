from src.utils.titan import titan
import requests
import time
import jwt
import discord
from datetime import datetime

questions = ['Timestamp', 'What is your Minecraft IGN?', 'What is your current rank in the guild (Ingame)?', 'What is your current rank in the guild discord?', 'How long have you been in ANO for?', 'Why do you want to become part of the war team?', 'What is the 1k mob defense that we put on our territories comprised of?', 'What is the basic 1k filler, not the one we defend on our territories (Yes, this is different than the previous question)', 'Briefly describe what a 22k is', "Please list the current FFA's (You don't have to list the exact name of the FFA)", 'Please check the territories that are a part of our claim', 'What is the name of the alliance that we are currently in?', 'Please list at least 7 guilds that are in this alliance that we are in', "List some of ANO's enemies", 'What is a Sub Guild and what is the purpose of a Sub Guild?', 'What does "Sniping" mean?', 'What is the name of our Guild Leader?', 'You are the only person online in ANO and you are in the middle of running LI. You see that 4 of our territories are attacked simultaneously. You look into your inventory and bank and realize that you have no scrolls. You were just about to get off Wynn and go to bed. WHAT DO YOU DO!!!', "You are warring against an enemy that has taken control of our allies claims, when the leader of this enemy guild messages you angrily. He threatens to bring the demise of your guild and goes on to rant about why you shouldn't pursue attacking. You are only person online with the highest rank in ANO so it is reasonable that he messages you. You are fairly new to the guild scene and don't know that much. WHAT DO YOU DO!!!!", "You are, once again, the only person online in ANO and you are fairly new to warring. You are warring some sweet FFA's when a person who you don't recognize messages you and tells you that there is a brand new FFA. They tell you that it is now an FFA because it was owned by an old guild that was wiped from the map. They say that the big alliance has decided to split up most of the old guilds claims but decided to make one  of the territories an FFA. WHAT DO YOU DO!!!", 'You are the only person online in ANO and you are warring some sweet FFAs when you see that one of your allies (in this big alliance) is being wiped. WHAT DO YOU DO!!!!']
def create_embed(row):
    embed = discord.Embed(title=row[1]+"\'s Captain Application", color=0x00eb0c)
    # embed.timestamp = datetime.datetime.utcnow()
    # embed.author = app[0][1]
    embed.description = '\n'.join("**"+questions[x][:50]+":\n**"+row[x][:50] for x in range(1, len(questions)))
    id = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{row[1]}").json()["id"]
    embed.set_thumbnail(url=f"https://crafatar.com/renders/body/{id}")
    embed.timestamp = datetime.strptime(row[0], "%m/%d/%Y %X")
    return embed

async def new_capt_apps(chn, client: discord.client):
    url = "https://oauth2.googleapis.com/token"
    pay = {
        "iss": titan.cred["client_email"],
        "scope": "https://www.googleapis.com/auth/spreadsheets",
        "aud": "https://oauth2.googleapis.com/token",
        "exp": int(time.time())+3600,
        "iat": int(time.time())
    }
    a = jwt.encode(pay, titan.cred["private_key"], algorithm='RS256')
    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": str(a)[2:-1]
    }
    r = requests.post(data=payload, url=url).json()
    access = r["access_token"]
    a = requests.get(url="https://sheets.googleapis.com/v4/spreadsheets/1xptBPOJ0F8M3geEtgX2ZYW7EG9MrR1OzJnwUiZV8Xzg/values/A1:Z1000", headers={"Authorization": "Bearer "+access}).json()
    new = []
    for row in a["values"][1:]:
        ign = row[1]
        if not ign in titan.appcache["cached_captapp"]:
            em = create_embed(row)
            await chn.send(embed=em)
            titan.appcache["cached_captapp"].append(ign)
            new.append(row)
    titan.save_apply()

    return new