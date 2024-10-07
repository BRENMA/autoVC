from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

from io import BytesIO
from PIL import Image
import time
import re
import os

numbersRe = re.compile(r'\d+(?:\.\d+)?')

def getDeckImg(url):
    driver = webdriver.Chrome()

    driver.get(url)
    time.sleep(1)

    try:
        companiesTemp = driver.find_element(By.TAG_NAME, 'body').text
        if "requests your action to continue" in companiesTemp:
            email_input = driver.find_element(By.XPATH, '//*[@id="link_auth_form_email"]')
            email_input.send_keys(os.environ.get("EMAIL_FOR_DOCSEND"))
            time.sleep(1)

            if "Passcode" in companiesTemp:
                password = input("Password: ")
                password_input = driver.find_element(By.XPATH, '//*[@id="link_auth_form_passcode"]')
                password_input.send_keys(password)
                password_input.send_keys(Keys.ENTER)
                time.sleep(1)
            else:
                email_input.send_keys(Keys.ENTER)

        time.sleep(2)

        numberOfPagesRaw = driver.find_element(By.XPATH, '//*[@id="toolbar"]/div[2]/div[1]').text
        numberOfPagesAll = numbersRe.findall(numberOfPagesRaw)
        numberOfPages = numberOfPagesAll[-1]
        numberOfPages = int(numberOfPages)
        
        time.sleep(2)

        element  = driver.find_element(By.XPATH, '//*[@class="viewer_content-container"]')
        location = element.location
        size = element.size

        i = 1
        while i <= numberOfPages:
           
            png = driver.get_screenshot_as_png()

            im = Image.open(BytesIO(png))

            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']

            im = im.crop((left, top, right, bottom)) # defines crop points
            im.save('./SCREEN_SHOTS/' + str(i) + '.png') # saves new cropped image

            time.sleep(1)

            driver.find_element(By.XPATH, '//*[@id="nextPageIcon"]').click()
            time.sleep(1)
            i+=1

    except Exception as e:
        print(e)

    driver.quit()