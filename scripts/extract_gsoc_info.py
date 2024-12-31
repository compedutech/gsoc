
from google.colab import drive
drive.mount('/content/drive')
import pandas as pd
from bs4 import BeautifulSoup
import time

# Commented out IPython magic to ensure Python compatibility.
# %pip install selenium
!apt-get update
!apt install chromium-chromedriver

from selenium import webdriver
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)

driver.get("https://summerofcode.withgoogle.com/archive/2020/projects/")

def extract_data(soup):

  all_a=soup.find_all('a')
  titles =soup.find_all(class_="title")
  descriptions=soup.find_all(class_ ="description")
  contibutors =soup.find_all(class_="contributor__content")
  mentors =soup.find_all(class_="mentor")
  organizations =soup.find_all(class_="organization")

  titles=[t.text if t is not None else "" for t in titles]
  descriptions=[d.text if d is not None else "" for d in descriptions]
  contibutors=[c.text if c is not None else "" for c in contibutors]
  mentors=[m.text if m is not None else "" for m in mentors]
  organizations=[o.text if o is not None else "" for o in organizations]


  archives=[]
  links=[]
  for a in all_a:
    arch=a.find(class_="mdc-button")
    p_a=a.get("class")
    if p_a is not None:
      if len(p_a)>1:
        if p_a[1]=="mdc-button--unelevated":
          archives.append(a.get('href'))
        elif p_a[1]=="mdc-button--outlined":
          links.append(a.get('href'))

  return titles,descriptions,contibutors,mentors,organizations,archives,links

#button =driver.find_element(By.CLASS_NAME,"mat-mdc-paginator-navigation-next").click()

found = True
j=0
while found:
    output=pd.DataFrame(columns=["Id","Title","Description","Contributor","Mentor","Organization","Archive","Github"])
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        titles,descriptions,contibutors,mentors,organizations,archives,links=extract_data(soup)
        j+=1
        #print(j)
        for i in range(len(titles)):
            result=[]
            result.append(i+1)
            lt=len(titles)
            ld=len(descriptions)
            lc=len(contibutors)
            lm=len(mentors)
            lo=len(organizations)
            la=len(archives)
            ll=len(links)

            if i<lt:
              result.append(titles[i])
            else:
              result.append("")
            if i<ld:
              result.append(descriptions[i])
            else:
              result.append("")
            if i<lc:
              result.append(contibutors[i])
            else:
              result.append("")
            if i<lm:
              result.append(mentors[i])
            else:
              result.append("")
            if i<lo:
              result.append(organizations[i])
            else:
              result.append("")
            if i<la:
              result.append(archives[i])
            else:
              result.append("")
            if i<ll:
              result.append(links[i])
            else:
              result.append("")
            #output.loc[i]=[i+1,titles[i],descriptions[i],contibutors[i],mentors[i],organizations[i],archives[i],links[i]]
            print(i)
            output.loc[i]=result
        print(j)
        time.sleep(5)
        #print(j)
        button =driver.find_element(By.CLASS_NAME,"mat-mdc-paginator-navigation-next")
        button.click()
        print("test 2")

        name="/content/drive/My Drive/summer_code_2020_"+str(j)+".csv"
        output.to_csv(name,index=False)
        if button.get_attribute("disabled"):
            found = False
        time.sleep(5)
    except:
        name="summer_code_2020_"+str(i)+".csv"
        output.to_csv(name,index=False)
        found = False
        print("error occurred")
        print(j)

soup = BeautifulSoup(driver.page_source, 'html.parser')
titles,descriptions,contibutors,mentors,organizations,archives,links=extract_data(soup)
output=pd.DataFrame(columns=["Id","Title","Description","Contributor","Mentor","Organization","Archive","Github"])
for i in range(len(titles)):
            result=[]
            result.append(str(j))
            if titles[i] is not None:
              result.append(titles[i])
            else:
              result.append("")
            if descriptions[i] is not None:
              result.append(descriptions[i])
            else:
              result.append("")
            if contibutors[i] is not None:
              result.append(contibutors[i])
            else:
              result.append("")
            if mentors[i] is not None:
              result.append(mentors[i])
            else:
              result.append("")
            if organizations[i] is not None:
              result.append(organizations[i])
            else:
              result.append("")
            if archives[i] is not None:
              result.append(archives[i])
            else:
              result.append("")
            if links[i] is not None:
              result.append(links[i])
            else:
              result.append("")
            #output.loc[i]=[i+1,titles[i],descriptions[i],contibutors[i],mentors[i],organizations[i],archives[i],links[i]]
            output.loc[i]=result
#output.loc[i]=[i+1,titles[i],descriptions[i],contibutors[i],mentors[i],organizations[i],archives[i],links[i]]
name="/content/drive/My Drive/summer_code_2020_last.csv"
output.to_csv(name,index=False)

driver.quit()

