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
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_pandas import Spread


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('My Project 53889-05501a7fa707.json', scope)

gc = gspread.authorize(credentials)

class Scraper:
    
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(executable_path=r'C:/Users/Abdul Rehman/Downloads/geckodriver-v0.26.0-win64/geckodriver.exe',options=options)
        now = datetime.datetime.now()
        self.date = now.strftime("%Y.%m.%d")
        self.data = pd.DataFrame(columns=['check_in','check_out','listing_id', 'price', 'url','cleaning_fee','service_fee','host','bedrooms'])
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
        #self.location = input("Please enter your location: ")
        self.adults = input("Please enter the number of adults: ")
        self.children = input("Please enter the number of children: ")
        self.infants = input("Please enter the number of infants: ")
        url = "https://www.airbnb.com.au/s/homes?host_id=36410227&refinement_paths%5B%5D=%2Fhomes&federated_search_session_id=8e26df57-cc2c-42e4-a03e-77cb05dc5807&search_type=unknown&tab_id=home_tab&checkin=" + self.check_in + "&checkout=" + self.check_out + "&adults=" + self.adults + "&map_toggle=false&children=" + self.children + "&infants=" + self.infants + "&min_bedrroms=1"
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
            new_row["check_in"] = self.check_in
            new_row["check_out"] = self.check_out
            new_row["listing_id"] = listing_id
            



            #print(listing_id)
            price = container.find("span",{"class":"_1p7iugi"}).text
            url =  "https://www.airbnb.com.au" + container.a["href"]
            new_row["url"] = url
            if len(re.findall('\d*\.?\d+,\d*\.?\d+',price)) >= 1:
                price = re.findall('\d*\.?\d+,\d*\.?\d+',price)[0]
                price = price.replace(",", "")
                
            else:
                price = re.findall('\d*\.?\d+',price)[0]
            
            
            new_row["price"] = price

            if listing_id not in self.data["listing_id"].values:
                self.data = self.data.append(new_row, ignore_index=True)
        
        #self.keepCrawling()

        #self.driver.close()

    def keepCrawling(self):

        #self.collectResults()
        counter = 0
        page = 0
        while True:

            try:
                page += 1
                print("Pages searched " + str(page))
                self.collectResults()
                counter += 20
                #if self.stop_crawling == False:
                self.driver.get("https://www.airbnb.com.au/s/homes?host_id=36410227&refinement_paths%5B%5D=%2Fhomes&federated_search_session_id=8e26df57-cc2c-42e4-a03e-77cb05dc5807&search_type=unknown&tab_id=home_tab&checkin=" + self.check_in + "&checkout=" + self.check_out + "&adults=" + self.adults + "&map_toggle=false&children=" + self.children + "&infants=" + self.infants + "&items_offset=" + str(counter) + "&min_bedrooms=1")
                if counter > 100:
                    break
            except Exception as e:
                print(str(e))
                break

        self.data.to_excel("Results.xlsx")
        price = self.data["price"].values
        price = price.astype(np.float)
        print("The number of properties are: " + str(len(price)))
        print("The mean price is: "+ str(np.mean(price)))
        print("The max price is: "+ str(np.max(price)))
        print("The min price is: "+ str(np.min(price)))
        print("The standard deviation is "+ str(np.std(price)))
        



        #self.f.close()
        
        #self.driver.refresh()

        
        #self.collectResults()
    
    def checkIndividualProperties(self):
        self.data.set_index('listing_id')
        page_number = 0
        for ind in self.data.index: 
            page_number += 1
            property_url = self.data['url'][ind]
            self.driver.get(property_url)
            time.sleep(25)
            soup = BeautifulSoup(self.driver.page_source,'lxml')
            try:
                host_name = soup.findAll("div", {"class": "_8b6uza1"})
                print(host_name)
                host = host_name[0]
                self.data.set_value(ind,'host',host.text)
            except Exception as e:
                print(str(e))

            try:
                price_structure = soup.findAll("span", {"class": "_j1kt73"})
                print(price_structure)
                print(len(price_structure))
                if len(price_structure) == 5:
                    cleaning_fee = price_structure[2]
                    cleaning_fee = cleaning_fee.text
                    if len(re.findall('\d*\.?\d+,\d*\.?\d+',cleaning_fee)) >= 1:
                        clean_fee = re.findall('\d*\.?\d+,\d*\.?\d+',cleaning_fee)[0]
                        clean_fee = clean_fee.replace(",", "")
                    else:
                        clean_fee = re.findall('\d*\.?\d+',cleaning_fee)[0]
                    self.data.set_value(ind,'cleaning_fee',clean_fee)
            except Exception as e:
                print(str(e))

            try:
                service_fee_exisits = False
                if len(price_structure) == 5:
                    service_fee = price_structure[3]
                    service_fee_exisits = True
                elif len(price_structure) == 4:
                    service_fee = price_structure[2]
                    service_fee_exisits = True
                
                if service_fee_exisits:
                    service_fee = service_fee.text
                    if len(re.findall('\d*\.?\d+,\d*\.?\d+',service_fee)) >= 1:
                        serv_fee = re.findall('\d*\.?\d+,\d*\.?\d+',service_fee)[0]
                        serv_fee = serv_fee.replace(",", "")
                    else:
                        serv_fee = re.findall('\d*\.?\d+',service_fee)[0]
                    
                    self.data.set_value(ind,'service_fee',serv_fee)
            except Exception as e:
                print(str(e))
            
            
            try:
                total = None
                if len(price_structure) == 5:
                    total = price_structure[4]
                elif len(price_structure) == 4:
                    total = price_structure[3]
                elif len(price_structure) == 2:
                    total = price_structure[1]
                 
                total = total.text
                if len(re.findall('\d*\.?\d+,\d*\.?\d+',total)) >= 1:
                    total_fee = re.findall('\d*\.?\d+,\d*\.?\d+',total)[0]
                    total_fee = total_fee.replace(",", "")
                else:
                    total_fee = re.findall('\d*\.?\d+',total)[0]
                
                self.data.set_value(ind,'total_fee',total_fee)
            except Exception as e:
                print(str(e))

            try:
                bedrooms = None
                bedroom_bathroom = soup.findAll("div", {"class": "_czm8crp"})
                bedrooms = bedroom_bathroom[0]
                bedrooms = bedrooms.text
                bedrooms = re.findall('\d+',bedrooms)[0]
                self.data.set_value(ind,'bedrooms',bedrooms)
            except Exception as e:
                print(str(e))   


            try:
                list_price = price_structure[2]
                list_price = list_price.text
                if len(re.findall('\d*\.?\d+,\d*\.?\d+',list_price)) >= 1:
                    list_price = re.findall('\d*\.?\d+,\d*\.?\d+',list_price)[0]
                    list_price = list_price.replace(",", "")
                else:
                    list_price = re.findall('\d*\.?\d+',list_price)[0]

                self.data.set_value(ind,'price',list_price)
            except Exception as e:
                print(str(e))   

            print("Page number " + str(page_number))
        
        spreadsheet_key = Spread("https://docs.google.com/spreadsheets/d/15_YZB-LVAa2NkHORZ8nvBq25YBj4R7ZUHjY11HRl0R4/edit#gid=0")
        spreadsheet_key.df_to_sheet(self.data, index=False, sheet=("MadeComfy "+self.date))

    def testSoup(self):
        self.driver.get("https://www.airbnb.com.au/rooms/35884342?location=Bondi%2C%20Australia&adults=1&check_in=2020-03-26&check_out=2020-03-28&source_impression_id=p3_1584146389_pqAE1Kx7nZu0obBe")
        time.sleep(10)
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        host_name = soup.findAll("div", {"class": "_8b6uza1"})
        print(host_name)
        host = host_name[0]
        print(host.text)
        host_id = soup.findAll("a", {"class": "_16lonkd"})
        host_id = host_id[0]
        host_id = host_id["href"]
        host_id = re.findall('\d+',host_id)[0]
        print(host_id)
        price_structure = soup.findAll("span", {"class": "_j1kt73"})
        print(price_structure)
        print(len(price_structure))
        cleaning_fee = price_structure[2]
        cleaning_fee = cleaning_fee.text
        if len(re.findall('\d*\.?\d+,\d*\.?\d+',cleaning_fee)) >= 1:
            clean_fee = re.findall('\d*\.?\d+,\d*\.?\d+',cleaning_fee)[0]
            clean_fee = clean_fee.replace(",", "")
        else:
            clean_fee = re.findall('\d*\.?\d+',cleaning_fee)[0]
        
        print(clean_fee)

        service_fee = price_structure[3]
        service_fee = service_fee.text
        if len(re.findall('\d*\.?\d+,\d*\.?\d+',service_fee)) >= 1:
            serv_fee = re.findall('\d*\.?\d+,\d*\.?\d+',service_fee)[0]
            serv_fee = serv_fee.replace(",", "")
        else:
            serv_fee = re.findall('\d*\.?\d+',service_fee)[0]
        
        print(serv_fee)


        total = price_structure[4]
        total = total.text
        if len(re.findall('\d*\.?\d+,\d*\.?\d+',total)) >= 1:
            total_fee = re.findall('\d*\.?\d+,\d*\.?\d+',total)[0]
            total_fee = total_fee.replace(",", "")
        else:
            total_fee = re.findall('\d*\.?\d+',total)[0]
        
        print(total_fee)

        


airbnb_scraper = Scraper()

airbnb_scraper.inputPrompt()
airbnb_scraper.keepCrawling()
airbnb_scraper.checkIndividualProperties()

#airbnb_scraper.testSoup()


