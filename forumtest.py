import requests
from bs4 import BeautifulSoup

required_texts = ["In-Game Username", "Timezone", "Main class and level", "How often, and for how long", "What do you like doing in Wynncraft"]

def get_text(post_raw):
    txt = post_raw.find('blockquote', {'class':'messageText SelectQuoteContainer ugc baseHtml'})
    return txt.text.lstrip().replace('[/QUOTE]', '').rstrip()

def is_application(text):
    return all(x in text for x in required_texts)

url = "https://forums.wynncraft.com/threads/%E2%9C%AB%E2%8B%86-titans-valor-community-war-guild-%E2%99%94-recruiting-all-1.206094/page-"
at = 37
already_applied = {}
forum_req_nxt = requests.get(url + str(at+1))
soup = BeautifulSoup(forum_req_nxt.text, 'lxml')
most_recent = int(soup.find('a', {'class': 'currentPage'}).text)
if most_recent != at:
    at = most_recent
    print("NOT MOST RECENT UPDATING...")
    forum_req_nxt = requests.get(url + str(at))
    soup = BeautifulSoup(forum_req_nxt.text, 'lxml')
posts_raw = soup.find('ol', {'id':'messageList'}).find_all('li', {'class': 'message'})
#posts_notq = [[get_text(x) for x in posts_raw if not x.find('blockquote', {'class': 'quoteContainer'}) and is_application(get_text(x))]]
posts_notq = []
for raw in posts_raw:
    txt = get_text(raw)
    if not raw.find('blockquote', {'class': 'quoteContainer'}) and is_application(txt):
        posts_notq.append(txt)
#print('\n-------------------\n'.join(posts_notq))
