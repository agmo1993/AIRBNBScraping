from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import csv
import datetime
import os
import time
import re
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import pandas as pd
class Scraper:
    
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(executable_path=r'C:/Users/Abdul Rehman/Downloads/geckodriver-v0.26.0-win64/geckodriver.exe',options=options)
        now = datetime.datetime.now()
        self.date = now.strftime("%Y.%m.%d")
        self.data = pd.DataFrame(columns=['listing_id', 'price', 'url'])
        #self.f = open("cometic_test" + self.date + ".csv","w", encoding='utf8')
        #button = self.driver.find_element_by_xpath('//*[@class="emailReengagement_close_button"]')
        #button.click()
        self.stop_crawling = False

    """
    def sendQuery(self, queryList):
        query = ""
        for i in queryList:
            query += i
        self.driver.find_element_by_id("simpleSearchForm:fpSearch:input").send_keys(query)
        self.driver.find_element_by_id("simpleSearchForm:fpSearch:buttons").click()
        return True
    """

    def inputPrompt(self):
        self.check_in = input("Please enter check in date in YYYY-MM-DD format: ")
        self.check_out = input("Please enter check out date in YYYY-MM-DD format: ")
        self.location = input("Please enter your location: ")
        url = "https://www.airbnb.com.au/s/" + self.location + "--Australia/homes?refinement_paths%5B%5D=%2Fhomes&query=" + self.location + "&search_type=unknown&map_toggle=false&checkin=" + self.check_in +"&checkout="+ self.check_out
        self.driver.get(url)

    def formatResultsPage(self):
        select_relevance = Select(self.driver.find_element_by_css_selector('select.ps-plain-select--input '))
        select_relevance.select_by_index(1)
        
        """
        select_max_results = Select(self.driver.find_element_by_id("resultListCommandsForm:perPage:input"))
        select_max_results.select_by_value("200")
        """
        """
        ------------------FIX ABOVE TO GET 200 RESULTS PER PAGE---------------------
        """
        #self.driver.refresh()
        return True

    def collectResults(self):

        soup = BeautifulSoup(self.driver.page_source,'lxml')
        containers = soup.findAll("div", {"class": "_1wz0grtk"})

        for container in containers:
            new_row = {}
            listing_id = container.a["target"]

            """
            if listing_id in self.data.values:
                self.stop_crawling = True
                break
            """
            new_row["listing_id"] = listing_id
            



            print(listing_id)
            price = container.find("span",{"class":"_1p7iugi"}).text
            url =  "https://www.airbnb.com.au" + container.a["href"]
            new_row["url"] = url
            if len(re.findall('\d*\.?\d+,\d*\.?\d+',price)) >= 1:
                price = re.findall('\d*\.?\d+,\d*\.?\d+',price)[0]
                price = price.replace(",", "")
                
            else:
                price = re.findall('\d*\.?\d+',price)[0]
            print(price)
            new_row["price"] = price

            self.data = self.data.append(new_row, ignore_index=True)
        
        #self.keepCrawling()

        #self.driver.close()

    def keepCrawling(self):

        #self.collectResults()
        counter = 0
        while True:

            try:
                self.collectResults()
                counter += 20
                #if self.stop_crawling == False:
                self.driver.get("https://www.airbnb.com.au/s/" + self.location + "--Australia/homes?refinement_paths%5B%5D=%2Fhomes&query=" + self.location + "&search_type=unknown&map_toggle=false&checkin=" + self.check_in +"&checkout="+ self.check_out + "&section_offset=3&items_offset=" + str(counter))
                if counter > 400:
                    break
            except Exception as e:
                print(str(e))
                break

        self.data.to_excel("Results.xlsx")

        self.driver.close()

        #self.f.close()
        
        #self.driver.refresh()

        
        #self.collectResults()

airbnb_scraper = Scraper()
airbnb_scraper.inputPrompt()
airbnb_scraper.keepCrawling()



