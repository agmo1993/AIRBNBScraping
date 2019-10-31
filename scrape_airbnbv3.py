from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import datetime
import os
import time
import re

os.chdir('C:\\Users\\Abdul Rehman\\Desktop\\Real Estate Scraping')

now = datetime.datetime.now()
date = now.strftime("%Y.%m.%d")

f = open("airbnb_test" + date + ".csv","w", encoding='utf8')

chrome_driver = r"C:\\Users\\Abdul Rehman\\Downloads\\chromedriver_win32\\chromedriver.exe"

driver = webdriver.Chrome(chrome_driver)

check_in = input("Please enter check in date in YYYY-MM-DD format")
check_out = input("Please enter check out date in YYYY-MM-DD format")

driver.get("https://www.airbnb.com.au/s/Sydney--New-South-Wales--Australia/homes?refinement_paths%5B%5D=%2Fhomes&query=Sydney%2C%20New%20South%20Wales%2C%20Australia&place_id=ChIJP3Sa8ziYEmsRUKgyFmh9AQM&search_type=unknown&map_toggle=false&checkin=" + check_in +"&checkout="+ check_out)

driver.fullscreen_window()

for i in range(0,30):
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(3)

soup = BeautifulSoup(driver.page_source,'lxml')

f.write("listing_id,price,"+ check_in +","+ check_out+"," + "url,\n")

containers = soup.findAll("div", {"class": "_y89bwt"})

for container in containers:
    listing_id = container["id"]
    price = container.find("span",{"class":"_1jlnvra2"}).text
    url =  "https://www.airbnb.com.au" + container.a["href"]
    if len(re.findall('\d*\.?\d+,\d*\.?\d+',price)) >= 1:
        price = re.findall('\d*\.?\d+,\d*\.?\d+',price)[0]
        price = price.replace(",", "")
    else:
        price = re.findall('\d*\.?\d+',price)[0]
    f.write(listing_id + "," + price + "," + check_in + "," + check_out + "," + url + "," + "\n")

f.close()



