from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd  
import time

import requests
import csv
import re

def pageScraper():
    driver = webdriver.Chrome()

    sheet = "urls.csv"

    urls = []
    with open(sheet, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for item in row:
                urls.append(item)
                print(item)

    for url in urls:
        driver.get(url)

        time.sleep(1)
        ht = driver.execute_script("return document.documentElement.scrollHeight;")
        while True:
            prev_ht=driver.execute_script("return document.documentElement.scrollHeight;")
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            ht=driver.execute_script("return document.documentElement.scrollHeight;")
            if prev_ht==ht:
                break

        current_url = driver.current_url
        print(current_url)

        fileTitle = re.sub(r'[^a-zA-Z ]', '', current_url)

        if '.pdf' in current_url:
            response = requests.get(current_url, stream = True)

            time.sleep(2)

            with open("./SOURCE_DOCUMENTS/" + fileTitle + ".pdf", 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)

        else:
            companiesTemp = driver.find_element(By.TAG_NAME, 'body').text
            txt = open("./SOURCE_DOCUMENTS/" + fileTitle + ".txt", 'w', encoding='utf8')
            txt.write(companiesTemp)
            txt.close()

    driver.close()
