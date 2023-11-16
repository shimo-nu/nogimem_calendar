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

# DB access
from nogi_db import NogiDB

load_dotenv()
console = Console()

# Settings
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--lang=ja-JP')

def getNogimember():
  


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
  
  
if __name__=='__main__':
  getNogimember()