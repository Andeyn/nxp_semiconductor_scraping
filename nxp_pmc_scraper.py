##################### IMPORT LIBRARIES #####################
from turtle import down
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import os
import csv
import pandas as pd
from parsel import Selector

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")

##################### DRIVER SET UP #####################
driver = webdriver.Chrome(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('headless')
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"
driver.set_window_size(1440,900)

######################## SPECS #########################
'''
--------------------
Processors and Microcontrollers (766)
-------------------
1. Retrieving all Product Categories and Subcategory
    - Arm Microcontrollers (368)
    - ARM® Processors (78)
    - Power Architecture (54)
    - Additional Architectures (95)
    - Legacy MCUs/MPUs (172)

2. Place all products in each category
    - Grab all links from <a id='datasheet-result'>
    - Use Dictionary Data Structure

3. Clean Data Set
    - drop all duplicates in each csv
'''

########################## CODE ##########################

# finds datasheet link on a single page
# returns list of links for each page
def get_href_per_page(href_lst):
    try:
        elements = driver.find_elements_by_class_name('resource-list')
    except:
        return href_lst
    for elem in elements:
        try:
            link = elem.find_element_by_xpath(".//*[@id='datasheet-result']")
            href = link.get_attribute('href')
            href_lst.append(href)    
        except:
            continue
    return href_lst

# scrapes all links, calling get_href_per_page(href_lst) and paginating
# returns df and writes new df into csv
def scrape_url(category, url, output_path):
    # set up driver 
    driver.get(url)
    
    href_lst = []
    pg_count = 1
    while pg_count < 65:
        try:
            get_href_per_page(href_lst)
            ################## PAGINATE ##################
            element = driver.find_element_by_class_name('icon-angle-right')
            driver.execute_script("arguments[0].click();", element)
            print(f'Navigating to Next Page {pg_count}')
            # print(f'href_lst: {href_lst}')
            pg_count += 1
            time.sleep(0.5)

        except (TimeoutException, WebDriverException) as e:
            print(f'error: {e}')
            print("Last page reached")
            break
    
    # puts it in a df and csv
    df = pd.DataFrame(href_lst, columns=['links'])
    # df.to_csv(output_path, index=True)
    return df

def main():
    # csv with all links [category, name, url]
    all_links_path = '/Users/andeyng/Desktop/semiconductors/ProcessorsAndMicrocontrollers.csv'
    df_all_links  = pd.read_csv(all_links_path)
    
    # iterating through each link
    for index, row in df_all_links.iterrows():
        filter = df_all_links.loc[index, 'filter']
        name = df_all_links.loc[index, 'name']
        url = df_all_links.loc[index, 'url']

        category = filter + '_' + name
        print(f'SCRAPING {category}')
        output_path = (f'/Users/andeyng/Desktop/semiconductors/nxp_pmc/{category}.csv')
        scrape_url(category, url, output_path)

    print(f'FINISHED SCRAPING ALL')

if __name__ == "__main__":
    main()
