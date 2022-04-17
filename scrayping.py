import requests
from bs4 import  BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import sys

# Settings
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-extensions')

# URL
nogizaka_member_url = "https://www.nogizaka46.com/s/n46/search/artist?ima=0123"
nogizaka_calendar_selector = "#md-sch > div.md--sc__in > div.md--sc__lists.js-md-sc.js-md-api > div"

# Selector
member_profile_cssselector = "#js-cont > main > div.mm--all.js-apimember > div > div.mm--list.js-apimember-list > div"
calendar_selector = "#md-sch > div.md--sc__in > div.md--sc__lists.js-md-sc.js-md-api > div"

# Variables
member_link_dict = {}
member_calendar_dict = {}

# Member List

## webdriver
nogi_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
nogi_driver.implicitly_wait(20)
nogi_driver.get(nogizaka_member_url)

## wait
time.sleep(3)

nogi_homepage_soup = BeautifulSoup(nogi_driver.page_source, 'html.parser')

## make member list
nogi_member_elems = nogi_homepage_soup.select(member_profile_cssselector)
for i in nogi_member_elems[:-1]:
    mem_name = i.find('p', class_="m--mem__name").get_text()
    link = i.find('a')
    member_link_dict[mem_name] = link.get('href')

print(member_link_dict.keys())
# Calendar

## Set member
member_name = "岩本 蓮加"
try:
    member_url = member_link_dict[member_name]
except KeyError:
    print("No member")
    sys.exit(1)
    
    
## webdriver
driver_mem = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
driver_mem.get(member_url)

## wait
time.sleep(3)

member_article_soup = BeautifulSoup(driver_mem.page_source, 'html.parser')

calendar_dict = {}
for i in member_article_soup.select(calendar_selector):
    day = i.find('p', class_="sc--day__d").text
    # contents = i.select('p', class_="m--scone__ttl")
    contents = i.find_all('div', class_="m--scone")
    
    
    title_list = []
    category_list = []
    content_list = []
    for content in contents:
        category = content.find('p', class_="m--scone__cat__name")
        time_duration = content.find('p', class_="m--scone__start")
        title = content.find('p', class_="m--scone__ttl") 
        
        article ={}
        if (category is not None):
            article["category"] = category.text
        if (time_duration is not None):
            article["duration"] = time_duration.text
        if (title is not None):
            article["title"] = title.text
                
        
        content_list.append(article)

    # article["title"] = title_list
    # article["category"] = category_list
    calendar_dict[day] = content_list
member_calendar_dict[member_name] = calendar_dict
print(calendar_dict)

