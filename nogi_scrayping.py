import requests
from bs4 import  BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome import service as fs
from selenium.common.exceptions import TimeoutException
import chromedriver_binary
import time
import sys, os
import re
import datetime
import argparse
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress

# DB access
from nogi_db import NogiDB

load_dotenv()
console = Console()

# Settings
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--lang=ja-JP')

def setNogimember():
  


  # URL
  nogizaka_member_url = "https://www.nogizaka46.com/s/n46/search/artist?ima=0123"

  # Selector
  member_profile_cssselector = "#js-cont > main > div.mm--all.js-apimember > div > div.mm--list.js-apimember-list > div"

  # Variables
  member_link_dict = {}

  # Member List

  ## webdriver
  # chrome_service = fs.Service(executable_path="/usr/")
  console.log("[Scrayping] Get HTML ...")
  nogi_driver = webdriver.Chrome(options=options)
  nogi_driver.implicitly_wait(20)
  nogi_driver.get(nogizaka_member_url)

  ## wait
  time.sleep(3)

  nogi_homepage_soup = BeautifulSoup(nogi_driver.page_source, 'html.parser')

  nogi_driver.quit()

  ## make member list
  console.log("[Scrayping] Creating Member List...")
  nogi_member_elems = nogi_homepage_soup.select(member_profile_cssselector)
  for i in nogi_member_elems[:-1]:
      mem_name = i.find('p', class_="m--mem__name").get_text()
      mem_name_kn = i.find('p', class_="m--mem__kn").get_text()
      link = i.find('a')
      member_link_dict[mem_name] = {"link": link.get('href'), "name_kn": mem_name_kn} 
  print(member_link_dict)
  data = [(key, value['link']) for key, value in member_link_dict.items()]

  # Work in progress
  # insert data ↑
  # if data exists in table, skip
  # and key is autoincrement data, so need to search the way for autoincrement.
  nogidb = NogiDB("TEST.db")
  
  nogidb.insert_data(data, "user")
  
def setNogiCalendar():
  calendar_selector = "#md-sch > div.md--sc__in"
  
  with NogiDB("TEST.db") as nogidb:
    nogi_members = nogidb.get_all_user(nogidb.db_connect)
  
  with Progress() as progress:
    task1 = progress.add_task("[red] Add Schedule to database...", total = len(nogi_members)+1)
    for member in nogi_members:
      progress.update(task1, advance=1, description=f"[red] Add Schedule to database...{member[1]}")   
      ## webdriver
      driver_mem = webdriver.Chrome(options=options)
      driver_mem.implicitly_wait(10)
      # driver_mem.set_window_size('1200', '1000')
      driver_mem.get(member[2])
      # element = driver_mem.find_element(By.CSS_SELECTOR, value=".js-lang-swich.ja")
      # print(element.is_displayed())
      # element.click()
      ## wait
      time.sleep(3)

      member_article_soup = BeautifulSoup(driver_mem.page_source, 'html.parser')

      # driver_mem.quit()

      calendar_dict = {}
      for i in member_article_soup.select(calendar_selector):
        contents = i.find_all('div', class_="sc--day")
        
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
            else:
                article["category"] = "no category"
            if (time_duration is not None):
                article["duration"] = time_duration.text
            if (title is not None):
                article["title"] = title.text
            else:
                article["title"] = "no title"
            if (url is not None):
                article["url"] = url
                match_txt = re.search(r'wd00=(\d{4}).*wd01=(\d{2}).*wd02=(\d{2})', url)

                if match_txt:
                    year, month, day = match_txt.groups()
                if "duration" in article:
                    start_time_str, end_time_str = article["duration"].split("〜")

                    start_hour, start_minute = map(int, start_time_str.split(":"))
                    if (end_time_str != ""):
                        end_hour, end_minute = map(int, end_time_str.split(":"))
                    else:
                        end_hour, end_minute = start_hour + 1, end_minute

                    day_offset_start = start_hour // 24
                    day_offset_end = end_hour // 24
                    start_hour %= 24
                    end_hour %= 24
                    year, month, day = int(year), int(month), int(day)
                    st_datetime = datetime.datetime(year, month, day, start_hour, start_minute) + datetime.timedelta(days=day_offset_start)
                    et_datetime = datetime.datetime(year, month, day, end_hour, end_minute) + datetime.timedelta(days=day_offset_end)
                    start_time = f"{st_datetime.year}-{st_datetime.month}-{st_datetime.day}-{st_datetime.hour}-{st_datetime.minute}"
                    end_time = f"{et_datetime.year}-{et_datetime.month}-{et_datetime.day}-{et_datetime.hour}-{et_datetime.minute}"
                    date = f"{year}-{month}-{day}"
                    article["date"] = [date, start_time, end_time]
                else:
                    date_only = f"{year}-{month}-{day}"
                    article["date"] = [date_only, 0, 0]

            content_list.append(article)
        with NogiDB("TEST.db") as nogidb:
          for content in content_list:

            date, st_time, end_time = content["date"]
            calendar_data = (member[0], date, st_time, end_time, content["category"], content["title"])
            nogidb.insert_user_calendar(nogidb.db_connect, calendar_data)
        

  
  
if __name__=='__main__':
  setNogimember()
  setNogiCalendar()