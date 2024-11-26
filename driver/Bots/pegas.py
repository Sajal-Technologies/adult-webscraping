from driver.get_driver import StartDriver
import json, random, os, time, requests, urllib, shutil, re
from utils.mail import SendAnEmail
from bs4 import BeautifulSoup
from app.models import cetegory, configuration, videos_collection, VideosData
from dateutil import parser
from datetime import datetime, timedelta
import pandas as pd

# selenium imports
from selenium.common.exceptions import NoSuchElementException, TimeoutException,ElementNotInteractableException,NoSuchElementException,WebDriverException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver


# captcha
from twocaptcha import TwoCaptcha



class Bot(StartDriver):
    def pegas_login(self):
        self.pegas = configuration.objects.get(website_name='pegas')
        self.pegas_category_path = self.create_or_check_path('pegas_category_videos')

        self.get_driver()
        # self.connect_vpn()
        # 'https://www.pegasproductions.com/front?lang=en&chlg=1&langue=en&nats='
        self.driver.get('https://www.pegasproductions.com/')

        
        if self.click_element('login btn', '//div[@class="connexion"]'):
            self.random_sleep()
            self.input_text(self.pegas.username, 'username','//input[@type="text"]')
            self.input_text(self.pegas.password, 'password','//input[@type="password"]')
            # self.click_element('username','//input[@type="submit"]')

            self.pegas_download_videos()
            # captcha part
            url = "https://members.5kporn.com/login"
            API_KEY = '6e00098870d05c550b921b362c2abde8'
            solver = TwoCaptcha(API_KEY)

            site_key_ele = self.find_element('SITE-KEY', 'g-recaptcha', By.CLASS_NAME)
            site_key = site_key_ele.get_attribute('data-sitekey')
            result = solver.recaptcha(sitekey=site_key, url=url)
            recaptcha_response = result['code']
            self.driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = arguments[0]',
                                       recaptcha_response)

            self.click_element('login btn', '//*[@type="submit"]')

            if self.find_element('Log out btn','//a[@href="https://pegasproductions.com/front/?logout=1"]') :
                self.get_cookies('pages')
                
                
    def pegas_download_videos(self):
        self.pegas.category
        all_cetegory = self.driver.find_elements(By.XPATH,'//*[@id="module-de-recherche-videos"]/div[2]/div[1]/div[1]/form/select/*')
        category = [i for i in all_cetegory if self.pegas.category.lower() in i.text.lower()]
        if not category:
            category = random.choice(all_cetegory[2:])
        else :
            category = category[0]

        category.click()
        allvideos = self.driver.find_elements(By.CLASS_NAME,"rollover_img_videotour")
        if allvideos : ...