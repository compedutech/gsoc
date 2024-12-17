import pandas as pd
from bs4 import BeautifulSoup
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By



chrome_options = webdriver.SafariOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Safari(options=chrome_options)

def isPull(url):
    if "pull" in url:
        return True
    return False

def extract_links(soup):
  all_a=soup.find_all('a')
  pull=[]
  issues=[]
  for a in all_a:
      link = a.get('href')
      if link is None:
          continue
      link_w= link.lower()
      if "github" in link_w:
          if "pull" in link_w:
              pull.append(link)
          elif "issues" in link_w:
              issues.append(link)
  return [pull,issues]


input_handle = open(r"/Users/popoolso/Desktop/summer_code_edit_2.csv", mode='r',encoding='UTF-8',newline='',errors='ignore')
handle_out = open(r"/Users/popoolso/Desktop/summer_code_out_2.csv", 'w', encoding='UTF-8', newline='')
writer_out = csv.writer(handle_out)
i=0
try:
    for line in csv.reader(input_handle):
        result=line
        i+=1
        if i%100==0:
            print(i)
        if line[7].startswith("http"):
            #print(line[7])
            if "pull" in line[7] or "issue" in line[7]:
                if "github" in line[7]:
                    result.append(line[7])
                    writer_out.writerow(result)
                    continue
            driver.get(line[7])
            time.sleep(7)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = extract_links(soup)
            result.append(links[0])
            result.append(links[1])
            
        writer_out.writerow(result)

except BaseException as e: 
    print(str(e))
    print("error")
    print(i)
input_handle.close()
handle_out.close()
