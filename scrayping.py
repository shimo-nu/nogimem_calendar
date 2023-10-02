import requests
from bs4 import  BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome import service as fs
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys, os
import re

from dotenv import load_dotenv
load_dotenv()


import add_calendar as ac
import datetime

# Settings
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--lang=ja-JP')

## Set member
member_name_ja = "岩本 蓮加"
member_name_en = "Renka Iwamoto"

# URL
nogizaka_member_url = "https://www.nogizaka46.com/s/n46/search/artist?ima=0123"
nogizaka_calendar_selector = "#md-sch > div.md--sc__in > div.md--sc__lists.js-md-sc.js-md-api > div"

# Selector
member_profile_cssselector = "#js-cont > main > div.mm--all.js-apimember > div > div.mm--list.js-apimember-list > div"
calendar_selector = "#md-sch > div.md--sc__in"

# Variables
member_link_dict = {}
member_calendar_dict = {}

# Member List

## webdriver
# chrome_service = fs.Service(executable_path=
nogi_driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
nogi_driver.implicitly_wait(20)
nogi_driver.get(nogizaka_member_url)

## wait
time.sleep(3)

nogi_homepage_soup = BeautifulSoup(nogi_driver.page_source, 'html.parser')

## make member list
nogi_member_elems = nogi_homepage_soup.select(member_profile_cssselector)
for i in nogi_member_elems[:-1]:
    mem_name = i.find('p', class_="m--mem__name").get_text()
    mem_name_kn = i.find('p', class_="m--mem__kn").get_text()
    link = i.find('a')
    member_link_dict[mem_name] = {"link": link.get('href'), "name_kn": mem_name_kn} 

print(member_link_dict.keys())

# Calendar

if (member_name_en in member_link_dict.keys()):
    member_url = member_link_dict[member_name_en]["link"]
    member_name = member_link_dict[member_name_en]["name_kn"]
elif (member_name_ja in member_link_dict.keys()):
    member_url = member_link_dict[member_name_ja]["link"]
    member_name = member_link_dict[member_name_ja]["name_kn"]
else:
    print("No member")
    sys.exit(1)
print(f"url : {member_url}")
print(f"name : {member_name}")

    
## webdriver
driver_mem = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver_mem.implicitly_wait(10)
# driver_mem.set_window_size('1200', '1000')
driver_mem.get(member_url)
# element = driver_mem.find_element(By.CSS_SELECTOR, value=".js-lang-swich.ja")
# print(element.is_displayed())
# element.click()
## wait
time.sleep(3)

member_article_soup = BeautifulSoup(driver_mem.page_source, 'html.parser')

calendar_dict = {}
for i in member_article_soup.select(calendar_selector):
    # contents = i.select('p', class_="m--scone__ttl")
    contents = i.find_all('div', class_="sc--day")
    
    title_list = []
    category_list = []
    content_list = []
    for content in contents:
        day = content.find('p', class_="sc--day__d").text
        category = content.find('p', class_="m--scone__cat__name")
        time_duration = content.find('p', class_="m--scone__start")
        title = content.find('p', class_="m--scone__ttl") 
        url = content.find('a', class_="m--scone__a").get("href")

        
        article ={}

        if (category is not None):
            article["category"] = category.text
        if (time_duration is not None):
            article["duration"] = time_duration.text
        if (title is not None):
            article["title"] = title.text
        if (url is not None):
            article["url"] = url
            match_txt = re.search(r'wd00=(\d{4}).*wd01=(\d{2}).*wd02=(\d{2})', url)

            if match_txt:
                year, month, day = match_txt.groups()
            if "duration" in article:
                print(article["duration"])
                start_time_str, end_time_str = article["duration"].split("〜")

                start_hour, start_minute = map(int, start_time_str.split(":"))
                end_hour, end_minute = map(int, end_time_str.split(":"))
                day_offset_start = start_hour // 24
                day_offset_end = end_hour // 24
                start_hour %= 24
                end_hour %= 24
                year, month, day = int(year), int(month), int(day)
                st_datetime = datetime.datetime(year, month, day, start_hour, start_minute) + datetime.timedelta(days=day_offset_start)
                et_datetime = datetime.datetime(year, month, day, end_hour, end_minute) + datetime.timedelta(days=day_offset_end)
                start_time = f"{st_datetime.year}-{st_datetime.month}-{st_datetime.day}-{st_datetime.hour}-{st_datetime.minute}"
                end_time = f"{et_datetime.year}-{et_datetime.month}-{et_datetime.day}-{et_datetime.hour}-{et_datetime.minute}"
                article["date"] = [start_time, end_time]
            else:
                date_only = f"{year}-{month}-{day}"
                article["date"] = [date_only]

        content_list.append(article)

    member_calendar_dict[member_name] = content_list

print(member_calendar_dict)

## Add Schedule
for content in member_calendar_dict[member_name]:
    if ("date" not in content):
        sys.exit(1)
    ### All day
    elif (len(content["date"]) == 1):
        print("add schedule which title is {}, date is {}".format(content["title"], content["date"]))
        ac.add_schedule(os.getenv("CALENDARID"), content["date"][0], content["date"][0], content["title"],  content["url"], all_day = True)
    elif (len(content["date"]) == 2):
        print("add schedule which title is {}, date is {}".format(content["title"], content["date"]))
        ac.add_schedule(os.getenv("CALENDARID"), content["date"][0], content["date"][1], content["title"], content["url"])


