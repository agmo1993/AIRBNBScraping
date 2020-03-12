from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import csv
import datetime
import os
import time
import re

os.chdir('C:\\Users\\Abdul Rehman\\Documents\\GitHub\\AIRBNBScraping')

now = datetime.datetime.now()
date = now.strftime("%Y.%m.%d")

options = Options()
options.add_argument("--headless")

f = open("airbnb_test" + date + ".csv","w", encoding='utf8')

#chrome_driver = r"C:\\Users\\Abdul Rehman\\Downloads\\chromedriver_win32\\chromedriver.exe"

driver = webdriver.Firefox(executable_path=r'C:/Users/Abdul Rehman/Downloads/geckodriver-v0.26.0-win64/geckodriver.exe')

check_in = input("Please enter check in date in YYYY-MM-DD format")
check_out = input("Please enter check out date in YYYY-MM-DD format")

driver.get("https://www.airbnb.com.au/s/Sydney--New-South-Wales--Australia/homes?refinement_paths%5B%5D=%2Fhomes&query=Sydney%2C%20New%20South%20Wales%2C%20Australia&place_id=ChIJP3Sa8ziYEmsRUKgyFmh9AQM&search_type=unknown&map_toggle=false&checkin=" + check_in +"&checkout="+ check_out)

driver.fullscreen_window()

SCROLL_PAUSE_TIME = 0.5

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

soup = BeautifulSoup(driver.page_source,'lxml')

f.write("listing_id,price,"+ "check_in" +","+ "check_out"+"," + "url,\n")

containers = soup.findAll("div", {"class": "_1wz0grtk"})

for container in containers:
    listing_id = container.a["target"]
    print(listing_id)
    price = container.find("span",{"class":"_1p7iugi"}).text
    print(price)
    url =  "https://www.airbnb.com.au" + container.a["href"]
    if len(re.findall('\d*\.?\d+,\d*\.?\d+',price)) >= 1:
        price = re.findall('\d*\.?\d+,\d*\.?\d+',price)[0]
        price = price.replace(",", "")
        
    else:
        price = re.findall('\d*\.?\d+',price)[0]
    f.write(listing_id + "," + price + "," + check_in + "," + check_out + "," + url + "," + "\n")

f.close()



