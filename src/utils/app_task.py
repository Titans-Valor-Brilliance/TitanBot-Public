from src.utils.titan import titan
from src import FORUMURL
import asyncio
import requests
from bs4 import BeautifulSoup
from discord import Embed
import datetime
from src.utils import sheets


def parse_app(text):
    app = [[x[:x.find(":")], x[x.find(":")+1:]]
                      for x in text.replace("\u200b", "\n").split("\n")]
    return app


def create_embed(app, txt, pfp):
    embed = Embed(title=app[0][1]+"\'s Application", color=0x00eb0c)
    # embed.timestamp = datetime.datetime.utcnow()
    # embed.author = app[0][1]
    embed.description = '\n'.join("**"+x[0]+"**"+x[1] for x in app)
    embed.set_thumbnail(url=f"https://forums.wynncraft.com/{pfp}")
    return embed


async def checkforums(chn, client):
    required_texts = ["IGN (In-Game Username):", "Timezone", "class",
                      "Activity", "What do you like doing in Wynncraft"]
    def get_text(post_raw):
        txt = post_raw.find(
            'blockquote', {'class': 'messageText SelectQuoteContainer ugc baseHtml'})
        return txt.text.lstrip().replace('[/QUOTE]', '').rstrip()

    def is_application(text):
        return all(x in text for x in required_texts)
    titan.update()
    already_applied = {}
    forum_req_nxt = requests.get(FORUMURL + str(titan.config['at']+1))
    soup = BeautifulSoup(forum_req_nxt.text, 'lxml')
    most_recent = int(soup.find('a', {'class': 'currentPage'}).text)
    if most_recent != titan.config['at']:
        titan.config['at'] = most_recent
        titan.save()
        print("NOT MOST RECENT UPDATING...")
        forum_req_nxt = requests.get(FORUMURL + str(titan.config['at']))
    soup = BeautifulSoup(forum_req_nxt.text, 'lxml')
    posts_raw = soup.find('ol', {'id': 'messageList'}).find_all(
            'li', {'class': 'message'})
    # posts_notq = [[get_text(x) for x in posts_raw if not x.find('blockquote', {'class': 'quoteContainer'}) and is_application(get_text(x))]]
    posts_notq = []
    for raw in posts_raw:
        txt = get_text(raw)
        app = parse_app(txt)
        name = app[0][1]
        pfp = raw.find('img', {'width': 96, 'height': 96})['src']
        if not raw.find('blockquote', {'class': 'quoteContainer'}) and is_application(txt) and not name in titan.appcache['cached_names']:
            titan.appcache['cached_names'].append(name)
            titan.save_apply()
            await chn.send(embed=create_embed(app, txt, pfp))
            posts_notq.append(txt)
        

async def check_forum_task(client):
    await client.wait_until_ready()
    chn = client.get_channel(titan.config["appChn"])
    capt_chn = client.get_channel(titan.config["capChn"])
    while not client.is_closed():

        await checkforums(chn, client)
        await sheets.new_capt_apps(capt_chn, client)
        await asyncio.sleep(titan.config["appcheck"])
