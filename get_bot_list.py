from bs4 import BeautifulSoup, SoupStrainer
from caching import *

cache = CacheFile("cache.json", True)

# get the bot list
url = 'https://www.reddit.com/r/autowikibot/wiki/redditbots'
page = cache.CheckCache_Soup(url)

users = []
for link in page.find("table").find_all("a"):
    users.append(link.getText())

with open("bot_list.txt", 'w') as f:
    for u in users:
        f.write(u+'\n')

# get the banned user list
page = BeautifulSoup(open('suspiciousaccounts.html').read(), "html.parser")

users = []
for link in page.find("table").find_all("a"):
    users.append(link.getText())

with open("banned_user_list.txt", 'w') as f:
    for u in users:
        f.write(u+'\n')
