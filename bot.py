from operator import index
from selenium.common.exceptions import NoSuchElementException, TimeoutException,ElementNotInteractableException,NoSuchElementException,WebDriverException, StaleElementReferenceException
from utils import list_files_in_folder, check_csv_with_columns, add_data_in_csv, move_downloading_video_to_destination_after_download
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from anticaptchaofficial.recaptchav2proxyless import *
from main.utils import naughty_convert_relative_time, get_chrome_version
from main.models import configuration, send_mail
from selenium.webdriver.common.keys import Keys
from anticaptchaofficial.imagecaptcha import *
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from collections import defaultdict
from twocaptcha import TwoCaptcha
# from driver import open_vps_driver
# from seleniumbase import Driver
from urllib.parse import unquote
from selenium import webdriver
from bs4 import BeautifulSoup
from mail import SendAnEmail
from dateutil import parser
from tqdm import tqdm
import urllib.request
import pandas as pd
import requests
import random
import shutil
import time
import json
import os
import re

with open("config.json", "r") as file:
    config = json.load(file)

headless = config.get("headless")

class scrapping_bot():
    
    def __init__(self,brazzers_bot = False,vpn=False):

        self.server_link = 'http://159.223.134.27:8000/'
        self.emailss = [mail.email for mail in send_mail.objects.all()]

        self.extra_args = []
        self.base_path = os.getcwd()

        self.driver = ''
        self.driver_type = ''

        self.create_or_check_path('downloads',main=True)
        self.download_path = os.path.join(os.getcwd(),'downloads')
        [ os.remove(os.path.join(os.getcwd(),'downloads',i)) for i in os.listdir('downloads') if i.endswith('.crdownload')]

        self.csv_path = self.create_or_check_path('csv',main=True)
        self.cookies_path = self.create_or_check_path('cookies',main=True)
        
        self.brazzers = configuration.objects.get(website_name='brazzers')
        self.brazzers_category_path = self.create_or_check_path('brazzers_category_videos')

        self.vip4k = configuration.objects.get(website_name='vip4k')
        self.vip4k_category_path = self.create_or_check_path('vip4k_category_videos')

        self.handjob = configuration.objects.get(website_name='handjob')
        self.handjob_category_path = self.create_or_check_path('handjob_category_videos')

        self.naughty = configuration.objects.get(website_name='naughtyamerica')
        self.naughty_america_category_path = self.create_or_check_path('naughty_america_videos')

        self.make_csv()
        self.delete_old_videos()
        
        if brazzers_bot == True:
            self.brazzers_category_url = 'https://site-ma.brazzers.com/categories'
            
        self.all_csv_files = list_files_in_folder(os.path.join(os.getcwd(),'csv'))
        self.vpn = vpn

    def driver_arguments(self):
        self.options.add_argument('--lang=en')  
        self.options.add_argument("--enable-webgl-draft-extensions")
        self.options.add_argument('--mute-audio')
        self.options.add_argument("--ignore-gpu-blocklist")
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--disable-blink-features=AutomationControlled") 
 
        # Exclude the collection of enable-automation switches 
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        
        # Turn-off userAutomationExtension 
        self.options.add_experimental_option("useAutomationExtension", False) 
        if self.vpn :
            # self.options.add_extension('Urban-VPN-Proxy.crx')
            self.options.add_extension('Touch-VPN-Secure-and-unlimited-VPN-proxy.crx')

        prefs = {"credentials_enable_service": True,
                'profile.default_content_setting_values.automatic_downloads': 1,
                "download.default_directory" : f"{self.download_path}",
            'download.prompt_for_download': False, 
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True ,
            "profile.password_manager_enabled": True}
        self.options.add_experimental_option("prefs", prefs)
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--start-maximized')    
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--enable-javascript")
        self.options.add_argument("--enable-popup-blocking")
        self.options.add_argument("--incognito")

        # self.options.add_argument(f"download.default_directory={self.base_path}/downloads")
    
    def connect_touchvpn(self,):
        """ Will select any counrty from the following 
            1. US
            2. Canada
            3. Russian Federation
            4. Germany
            5. Netherland (Removed and will not connect now)
            6. UK
        """
        self.driver.get('chrome-extension://bihmplhobchoageeokmgbdihknkjbknd/panel/index.html')
        time.sleep(2)
        time.sleep(3)
        time.sleep(1)
        window_handles = self.driver.window_handles
        time.sleep(1)
        self.driver.switch_to.window(window_handles[0])
        time.sleep(1)
        self.driver.find_element(By.XPATH,'//*[@class="location"]').click()
        time.sleep(3)
        locations = self.driver.find_element(By.XPATH,'//*[@class="list"]')
        time.sleep(1)
        location = locations.find_elements(By.XPATH,'//*[@class="row"]')
        # location = [ i for i in location if not "Netherlands" == i.text]
        location[random.randint(6,6)].click()
        time.sleep(2)
        self.driver.find_element(By.XPATH,'//*[@id="ConnectionButton"]').click()
        wait = WebDriverWait(self.driver, 10)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[text()="Stop"]')))
        except Exception as e:
            print(f"Error: {e}")
        connected = self.driver.find_element(By.XPATH,'//*[text()="Stop"]')
        if connected:
            return True
        else:
            return False
        
    def set_extra_argument(self):
        if self.extra_args:
            for arg in self.extra_args:
                self.options.add_argument(arg)
    
    def get_driver(self,):
        headless = False
        if not headless:
            self.get_local_driver()
            return
            
        else:
            for _ in range(30):
                user_agents = [
                    # Add your list of user agents here
                    f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(108,126)}.0.0.0 Safari/537.36',
                    f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(108,126)}.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                ]

                if self.driver_type == 'normal':
                    from selenium import webdriver
                    for _ in range(30):
                        user_agent = random.choice(user_agents)
                        self.options = webdriver.ChromeOptions()
                        self.set_extra_argument()
                        self.options.add_argument(f'user-agent={user_agent}')
                        self.options.add_argument(f'--headless')
                        self.driver_arguments()
                        self.options.add_argument(f"download.default_directory={os.path.join(os.getcwd(), 'downloads')}")

                        try:
                            self.driver = webdriver.Chrome(options=self.options)
                            params = {
                                "behavior": "allow",
                                "downloadPath": os.path.join(os.getcwd(), 'downloads')
                            }
                            self.driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
                            break
                        except Exception as e:
                            print(e)
                else:
                    import undetected_chromedriver as uc
                    user_agent = random.choice(user_agents)
                    self.options = uc.ChromeOptions()
                    self.set_extra_argument()
                    self.options.add_argument(f'user-agent={user_agent}')
                    self.options.add_argument(f"download.default_directory={os.path.join(os.getcwd(), 'downloads')}")
                    try:
                        self.driver = uc.Chrome(use_subprocess=False, headless=True, version_main=get_chrome_version())
                        params = {
                            "behavior": "allow",
                            "downloadPath": os.path.join(os.getcwd(), 'downloads')
                        }
                        self.driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
                        break
                    except Exception as e:


                            print(e)
        
            return self.driver

    def get_local_driver(self):
        """### Start webdriver and return state of it.
            #### if not self.driver_type then it's by default go with undetected chromedriver,
            #### else use normal selenium driver with extra argument."""
        # import seleniumwire.undetected_chromedriver as uc
        user_agents = [
            # Add your list of user agents here
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        ]
        # self.driver_type = 'normal'
        if self.driver_type == 'normal':
            from selenium import webdriver
            for _ in range(30):
                user_agent = random.choice(user_agents)
                self.options = webdriver.ChromeOptions()
                self.set_extra_argument()
                self.options.add_argument(f'user-agent={user_agent}')
                self.driver_arguments()
                self.options.add_argument("--incognito")

                self.options.add_argument(f"download.default_directory={os.path.join(os.getcwd(),'downloads')}")
                try:
                    self.driver = webdriver.Chrome(options=self.options)
                    params = {
                        "behavior": "allow",
                        "downloadPath": os.path.join(os.getcwd(), 'downloads')
                    }
                    self.driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
                    break
                except Exception as e:
                    
                    print(e)
        else:
            import undetected_chromedriver as uc
            for _ in range(30):
                user_agent = random.choice(user_agents)
                self.options = uc.ChromeOptions()
                self.set_extra_argument()
                self.options.add_argument(f'user-agent={user_agent}')
                self.options.add_argument("--incognito")
                self.options.add_argument(f"download.default_directory={os.path.join(os.getcwd(),'downloads')}")

                try:
                    self.driver = uc.Chrome(use_subprocess=False)
                    params = {
                        "behavior": "allow",
                        "downloadPath": os.path.join(os.getcwd(),'downloads')
                    }
                    self.driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
                    break
                except Exception as e:
                    print(e)
        
        return self.driver
    
    def connect_vpn(self):
        self.connect_touchvpn()
        # self.connect_cyberghost_vpn()
        # self.driver.switch_to.window(self.driver.window_handles[0])
        # self.driver.get('chrome-extension://ffbkglfijbcbgblgflchnbphjdllaogb/index.html')
        # time.sleep(3)

        # # Disconnect if already connected
        # connected_btn = self.driver.find_elements(By.CLASS_NAME, 'dark outer-circle connected')
        # time.sleep(1)
        # connected_btn[0].click() if connected_btn else None
        # time.sleep(2)

        # # Select country
        # countries_drop_down_btn = self.driver.find_elements(By.TAG_NAME, 'mat-select-trigger')
        # time.sleep(1)
        # countries_drop_down_btn[0].click() if countries_drop_down_btn else None
        # time.sleep(2)
        # total_option_country = self.driver.find_elements(By.TAG_NAME, 'mat-option')
        # for i in total_option_country:
        #     i_id = i.get_attribute('id')
        #     time.sleep(1)
        #     country_text_ele = i.find_element(By.XPATH, f"//*[@id='{i_id}']/span")
            
        #     country_text = country_text_ele.text
        #     time.sleep(1)
        #     # checking if the country is whether same or not and click on it
        #     if vpn_country == country_text:
        #         time.sleep(1)
        #         print('connected country is :',vpn_country)
        #         country_text_ele.click()
        #         break
        # time.sleep(3)
        # # Checking is the VPN connected or not
        # connect_btn = self.driver.find_element(By.XPATH, '//div[@class="dark disconnected outer-circle"]')
        # connect_btn.click()
        # time.sleep(4)
      
    def delete_cache_folder(self,folder_path):
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print("Cache folder deleted successfully.")
        else:
            print("Cache folder not found.")

    def find_element(self, element, locator, locator_type=By.XPATH,
            page=None, timeout=10,
            condition_func=EC.presence_of_element_located,
            condition_other_args=tuple()):
        """Find an element, then return it or None.
        If timeout is less than or requal zero, then just find.
        If it is more than zero, then wait for the element present.
        """
        try:
            if timeout > 0:
                wait_obj = WebDriverWait(self.driver, timeout)
                ele = wait_obj.until(EC.presence_of_element_located((locator_type, locator)))
                # ele = wait_obj.until( condition_func((locator_type, locator),*condition_other_args))
            else:
                print(f'Timeout is less or equal zero: {timeout}')
                ele = self.driver.find_element(by=locator_type,
                        value=locator)
            if page:
                print(
                    f'Found the element "{element}" in the page "{page}"')
            else:
                print(f'Found the element: {element}')
            return ele
        except (NoSuchElementException, TimeoutException) as e:
            if page:
                print(f'Cannot find the element "{element}"'
                        f' in the page "{page}"')
            else:
                print(f'Cannot find the element: {element}')
                
    def click_element(self, element, locator, locator_type=By.XPATH,
            timeout=10):
        """Find an element, then click and return it, or return None"""
        ele = self.find_element(element, locator, locator_type, timeout=timeout)
        
        if ele:
            self.driver.execute_script('arguments[0].scrollIntoViewIfNeeded();',ele)
            self.ensure_click(ele)
            print(f'Clicked the element: {element}')
            return ele

    def input_text(self, text, element, locator, locator_type=By.XPATH,
            timeout=10, hide_keyboard=True):
        """Find an element, then input text and return it, or return None"""
        
        ele = self.find_element(element, locator, locator_type=locator_type,
                timeout=timeout)
        
        if ele:
            for i in range(3):
                try: 
                    ele.send_keys(text)
                    print(f'Inputed "{text}" for the element: {element}')
                    return ele    
                except ElementNotInteractableException :...
    
    def ScrollDown(self,px):
        self.driver.execute_script(f"window.scrollTo(0, {px})")
    
    def ensure_click(self, element: WebElement, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(element))
            element.click()
        except WebDriverException:
            self.driver.execute_script("arguments[0].click();", element)
        
    def new_tab(self):
        self.driver.find_element(By.XPATH,'/html/body').send_keys(Keys.CONTROL+'t')

    def random_sleep(self,a=3,b=7,reson = ""):
        random_time = random.randint(a,b)
        print('time sleep randomly :',random_time) if not reson else print('time sleep randomly :',random_time,f' for {reson}')
        time.sleep(random_time)

    def getvalue_byscript(self,script = '',reason=''):
        """made for return value from ele or return ele"""
        if reason :print(f'Script execute for : {reason}')
        else:
            print(f'execute_script : {script}')
        value = self.driver.execute_script(f'return {script}')  
        return value
        
    def CloseDriver(self):
        if isinstance(self.driver, WebDriver):
            self.driver.quit()
        print('Driver is closed !')
        
    def calculate_old_date(self, days = 30) : 
        """ get old date from today's by the accepting date and return datetime object"""
        today = datetime.now()
        self.old_date = today - timedelta(days=days)
        return self.old_date

    def date_older_or_not(self,date_string=''):
        if date_string :
            date_obj = parser.parse(date_string)
            return date_obj < self.old_date 
        return False

    def starting_bots(self):
        self.get_driver()
        return self.driver

    def connect_cyberghost_vpn(self):
        vpn_country_list = ['Romania','Netherlands','United States']
        vpn_country = random.choice(vpn_country_list)
        for  _ in range(3):
            self.driver.get('chrome-extension://ffbkglfijbcbgblgflchnbphjdllaogb/index.html')
            self.random_sleep()

            # Disconnect if already connected
            connected_btn = self.find_element('connected vpn circle','/html/body/app-root/main/app-home/div/div[2]/app-switch/div')
            if connected_btn :
                if not "disconnected" in connected_btn.get_attribute('class') : 
                    self.click_element('connected vpn circle','/html/body/app-root/main/app-home/div/div[2]/app-switch/div')
                    self.random_sleep()
                else: 
                    self.random_sleep(5,10)

            self.driver.execute_script('document.querySelector("body > app-root > main > app-home > div > div.servers.en > mat-form-field > div > div.mat-form-field-flex.ng-tns-c19-0 > div").click()')
            self.driver.execute_script('document.querySelector("body > div.cdk-overlay-container > div.cdk-overlay-backdrop.cdk-overlay-transparent-backdrop.cdk-overlay-backdrop-showing").click()')
            
            drop_down_ = self.click_element('country drop down','mat-select-trigger',By.TAG_NAME)       
            if not drop_down_ : 
                self.CloseDriver()
                self.get_driver()
                continue

            # selecting the country
            total_option_country = self.driver.find_elements(By.TAG_NAME, 'mat-option')
            for i in total_option_country:
                i_id = i.get_attribute('id')
                country_text_ele = i.find_element(By.XPATH, f"//*[@id='{i_id}']/span")
                country_text = country_text_ele.text

                # checking if the country is whether same or not and click on it
                if vpn_country in country_text:
                    print('connected country is :',vpn_country)
                    country_text_ele.click()
                    break
            time.sleep(1)
            # Checking is the VPN connected or not
            self.click_element('Connecting vpn circle','//div[@class="dark disconnected outer-circle"]')
            self.random_sleep()
            connected_btn = self.find_element('connected vpn circle','/html/body/app-root/main/app-home/div/div[2]/app-switch/div')
            if connected_btn :
                if not "disconnected" in connected_btn.get_attribute('class') : 
                    return

    def find_and_delete_video(self,folder_path, video_title):
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                base_name, extension = os.path.splitext(filename)
                if base_name == video_title:
                    file_path = os.path.join(foldername, filename)
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
        return

    def load_cookies(self,website :str, redirect_url:str=''):
        try:
            # if 'vip4k' in website:
            #     path = os.path.join(self.cookies_path,f'{website}_cookietest.json')
            #     if os.path.isfile(path):
            #         with open(path,'rb') as f:cookies = json.load(f)
            #         for item in cookies:
            #             if item.get("domain") == ".vip4k.com":
            #                 self.driver.add_cookie(item)
            # else:
            path = os.path.join(self.cookies_path,f'{website}_cookietest.json')
            if os.path.isfile(path):
                with open(path,'rb') as f:cookies = json.load(f)
                for item in cookies: self.driver.add_cookie(item)
            if redirect_url:self.driver.get(redirect_url)
            else:self.driver.refresh()
            self.random_sleep()                
        except : 
            SendAnEmail('The coockies could not be loaded')

    def get_cookies(self,website :str):
        path = os.path.join(self.cookies_path,f'{website}_cookietest.json')
        cookies = self.driver.get_cookies()
        with open(path, 'w', newline='') as outputdata:
            if website == "5kteen" :
                cookies[0]['expiry'] +=172800

            json.dump(cookies, outputdata)
        return cookies
            
    def brazzers_login(self):
        self.load_cookies(self.brazzers.website_name)
        while True :
            try:
                self.driver.get('https://site-ma.brazzers.com/store')
                break
            except Exception as  e: 
                print(e) 
                self.CloseDriver()
                self.get_driver()
                self.connect_touchvpn()
                # self.connect_cyberghost_vpn()
                # self.connect_cyberghost_vpn()
            
        while not self.driver.execute_script("return document.readyState === 'complete'"):pass
        
        self.random_sleep(5,7)
        if self.driver.current_url != "https://site-ma.brazzers.com/store":
            for _ in range(3):
                time.sleep(1.5)
                if not self.find_element('Login form','//*[@id="root"]/div[1]/div[1]/div/div/div/div/form/button') :
                    self.click_element('try again',"//a[@href='https://site-ma.brazzers.com' and @rel='nofollow']",timeout=5)
                    return False
                if self.find_element('Login form','//*[@id="root"]/div[1]/div[1]/div/div/div/div/form/button') :
                    self.input_text(str(self.brazzers.username),'Username','username',By.NAME)
                    self.input_text(str(self.brazzers.password),'password','password',By.NAME)
                    self.click_element('Submit','//button[@type="submit"]')
                    self.random_sleep(2,3)
                    for _ in range(4):
                        if "login" not in self.driver.current_url:
                            self.get_cookies(self.brazzers.website_name)
                            return True
                        self.random_sleep(2,3)
                self.driver.delete_all_cookies()
                self.driver.refresh()
            return False
        else :
            return True

    def brazzers_get_categories(self):
        if not self.driver.current_url.lower() == self.brazzers_category_url :
            self.driver.get(self.brazzers_category_url)
        found_category = False
        
        for i1 in range(1,6) :
            cate1 = self.find_element('category',f'//*[@id="root"]/div[1]/div[2]/div[3]/div[2]/div[2]/div[{i1}]/div/div/a',timeout= 1)
            if cate1 : 
                if cate1.text.lower() == self.brazzers.category.lower() :
                    time.sleep(1)
                    self.click_element('category', f'//*[@id="root"]/div[1]/div[2]/div[3]/div[2]/div[2]/div[{i1}]/div/div/a',timeout=1)
                    found_category = True
                    break 
        
        
        if found_category == False :
            for i2 in range(4,15):
                if self.find_element('catefory grid',f'//*[@id="root"]/div[1]/div[2]/div[3]/div[2]/div[{i2}]/div',timeout=5):
                    for i3 in range(1,6):
                        cate1 = self.find_element('category',f'//*[@id="root"]/div[1]/div[2]/div[3]/div[2]/div[{i2}]/div[{i3}]/div/div/a',timeout=1)
                        if cate1:
                            if cate1.text.lower() == self.brazzers.category.lower() :
                                found_category = True
                                self.click_element('category', f'//*[@id="root"]/div[1]/div[2]/div[3]/div[2]/div[{i2}]/div[{i3}]/div/div/a',timeout=1)
                                break
                else : break
                if found_category == True : break
        
        if found_category == True : 
            return True
        else: 
            return False
    
    def column_to_list(self,website_name : str,column_name :str)-> list:
        if '_videos' in website_name:website_name =website_name.replace('_videos','')
        df1 = pd.read_csv(os.path.join(self.csv_path,f'{website_name}_videos_details.csv'))
        list_of_column = df1[f'{column_name}'].values.tolist()
        return list_of_column
        
    def brazzers_get_videos_url(self):
        video_detailes = {'collection_name':'','video_list':[]}
        videos_urls = []
        
        self.calculate_old_date(self.brazzers.more_than_old_days_download)
        df_url = self.column_to_list(self.brazzers.website_name,'Url')
        page_number = 0
        driver_url = self.driver.current_url
        tags = driver_url.split('tags=')[-1]
        found_max_videos = self.brazzers.numbers_of_download_videos
        self.random_sleep(6,10)
        video_detailes['collection_name'] = self.get_collection_name()
        
        
        while len(videos_urls) < found_max_videos:
            all_thumb = self.driver.find_elements(By.XPATH,"//div[contains(@class, 'one-list-1vyt92m') and contains(@class, 'e1vusg2z1')]" )
            try :
                for thumb in all_thumb: 
                    video_date = thumb.find_element(By.XPATH, "//div[2]/div/div[2]/div/div[2]")
                    video_date = thumb.find_element(By.XPATH, "//div[contains(@class, 'one-list-1oxbbh0') and contains(@class, 'e1jyqorn27')]")
                    self.driver.execute_script("arguments[0].scrollIntoView();", video_date)
                    time.sleep(0.3)
                    if video_date and self.date_older_or_not(video_date.text) :                            
                            video_url = thumb.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            post_url = thumb.find_element(By.TAG_NAME, 'img').get_attribute('src')
                            if video_url and post_url and video_url not in df_url:
                                print(f'add video url in lists')
                                videos_urls.append({"video_url":video_url,'post_url':post_url})
                                if len(videos_urls) >= found_max_videos:
                                    break
            except Exception as e :
                print(e)
            if len(videos_urls) < found_max_videos:
                self.driver.get(f'https://site-ma.brazzers.com/scenes?page={page_number}&tags={tags}')
                self.random_sleep(2,4)
                page_number +=1
        
            
        video_detailes['video_list'] = videos_urls
        return video_detailes

    def set_data_of_csv(self,website_name :str, tmp :dict,video_name : str):
        if '_videos' in website_name:website_name =website_name.replace('_videos','')
        if 'addon_102' in website_name :
            website_name = 'brazzers_'+ 'mofos'
        if 'addon_152' in website_name :
            website_name = 'brazzers_'+ 'reality_kings'
        if 'addon_162' in website_name :
            website_name = 'brazzers_'+ 'brazzers_main'
        website_video_csv_path = os.path.join(self.csv_path,f'{website_name}_videos.csv')
        website_video_details_csv_path = os.path.join(self.csv_path,f'{website_name}_videos_details.csv')
        videos_collection = pd.read_csv(website_video_details_csv_path)
        videos_collection = videos_collection.to_dict(orient='records')
        videos_data = pd.read_csv(website_video_csv_path)
        videos_data = videos_data.to_dict(orient='records')
        videos_data.append({"Video-title": video_name,"video_url": tmp['video_download_url'],"downloaded_time": datetime.now()})    
        videos_collection.append(tmp)
        pd.DataFrame(videos_collection).to_csv(website_video_details_csv_path, index=False)
        pd.DataFrame(videos_data).to_csv(website_video_csv_path, index=False)

    def brazzers_download_video(self, videos_dict):
        videos_urls = videos_dict['video_list']
        collection_name = videos_dict['collection_name']
        collection_path = self.create_or_check_path(self.brazzers_category_path,sub_folder_=collection_name)
        for idx,videoss_urll in enumerate(videos_urls) :
            self.driver.get(videoss_urll['video_url'])
            self.random_sleep(10,15)
            video_name = self.sanitize_title(self.driver.current_url.split('https://site-ma.brazzers.com/')[-1])

            v_urllll = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
            p_urllll = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
            tmp = {
                "Likes" : "",
                "Disclike" :"",
                "Url" : videoss_urll['video_url'] ,
                "Category":str(collection_name).replace('_videos',''),
                "video_download_url" : v_urllll,
                "Title" : '',
                "Discription" : "",
                "Release-Date" : "",
                "Poster-Image_uri" : videoss_urll['post_url'],
                "poster_download_uri" : p_urllll,
                "Video-name" : f'{video_name}.mp4',
                "Photo-name" : f'{video_name}.jpg',
                "Pornstarts" : '',
                "Username" : self.brazzers.website_name,
            }
            try:
                response = requests.get(tmp['Poster-Image_uri'])
                with open(f'{collection_path}/{video_name}.jpg', 'wb') as f:f.write(response.content)
                likes_count = self.find_element('Likes count','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[1]/div/section/div[3]/div[1]/div[7]/span[1]/strong')
                if likes_count :
                    tmp['Likes'] = likes_count.text

                likes_count = self.find_element('Likes count','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[1]/div/section/div[3]/div[1]/div[7]/span[1]/strong')
                if likes_count :
                    tmp['Likes'] = likes_count.text
                
                # self.getvalue_byscript('document.querySelector("#root > div.sc-yo7o1v-0.hlvViO > div.sc-yo7o1v-0.hlvViO > div.sc-1fep8qc-0.ekNhDD > div.sc-1deoyo3-0.iejyDN > div:nth-child(1) > div > section > div.sc-1wa37oa-0.irrdH > div.sc-bfcq3s-0.ePiyNl > div.sc-k44n71-0.gbGmcO > span:nth-child(1) > strong").textContent')
                Disclike_count = self.find_element('Disclike count','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[1]/div/section/div[3]/div[1]/div[7]/span[2]/strong')
                if Disclike_count :
                    tmp['Disclike'] = Disclike_count.text

                Title = self.find_element('Title','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[5]/div/section/div/div/h2[2]')
                if Title :
                    tmp['Title'] = Title.text

                Release = self.find_element('Release','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[5]/div/section/div/div/h2[1]')
                if Release :
                    tmp['Release-Date'] = Release.text

                Discription = self.find_element('Discription','/html/body/div[1]/div[1]/div[2]/div[3]/div[2]/div[6]/div/section/div/p')
                if Discription :
                    tmp['Discription'] = Discription.text

                port_starts = self.find_element('pornstars','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[5]/div/section/div/div/div[2]/h2')
                if port_starts :
                    tmp['Pornstarts'] = port_starts.text

                self.click_element('download btn','//button[@class="sc-yox8zw-1 VZGJD sc-rco9ie-0 jnUyEX"]')
                self.click_element('download high_quality','//div[@class="sc-yox8zw-0 cQnfGv"]/ul/div/button[1]')
                file_name = self.wait_for_file_download()
                self.random_sleep(3,5)
                name_of_file = os.path.join(self.download_path, f'{video_name}.mp4')
                os.rename(os.path.join(self.download_path,file_name), name_of_file)
                self.random_sleep(2,4)
                self.copy_files_in_catagory_folder(name_of_file,collection_path)
                self.set_data_of_csv(self.brazzers.website_name,tmp,video_name=video_name)
            except Exception as e :
                print('Error :', e)

    def get_collection_name(self: str) -> str:
        name_of_collection = self.find_element('category name', '//h1')
        return name_of_collection.text.replace(' ', '_').lower() if name_of_collection else False

    def download_all_brazzer_channels_video(self):
        tags_dict = {
            "mofos_videos": 'addon=102',
            "reality_kings_videos": 'addon=152',
            "brazzers_main_videos": 'addon=162'
        }

        for collection, tag in tags_dict.items():
            video_dict = self.get_brazzers_videos_url(collection=collection, tag=tag)
            self.download_brazzer_videos(video_dict, Site_name=collection)

            
    def get_brazzers_videos_url(self,url=None, collection=None, tag=None):
        self.calculate_old_date(self.brazzers.more_than_old_days_download)
        video_detailes = {'collection_name':'','video_list':[]}
        videos_urls = []
        if collection:
            self.driver.get(f'https://site-ma.brazzers.com/scenes?{tag}')
        elif url:
            self.driver.get(url)
        else:
            if not self.brazzers_get_categories():
                return video_detailes

        found_max_videos = self.brazzers.numbers_of_download_videos
        self.random_sleep(6,10)
        collection_name = (f'{self.brazzers.category}_videos' if not collection else f'brazzers_{collection}').replace('brazzers_brazzers','brazzers')
        video_detailes['collection_name'] = collection_name        
        if collection:self.make_csv(collection_name,new=True) 
        csv_name = collection_name if collection else self.brazzers.website_name

        df_url = self.column_to_list(csv_name,'Url')

        while len(videos_urls) < found_max_videos:
            self.random_sleep(10,15)
            all_thumb = self.driver.find_elements(By.XPATH,"//div[contains(@class, 'one-list-1vyt92m') and contains(@class, 'e1vusg2z1')]" )
            try :
                for thumb in all_thumb: 
                    video_date = thumb.find_element(By.XPATH, ".//div/div[2]/div/div[2]")
                    self.driver.execute_script("arguments[0].scrollIntoView();", video_date)
                    time.sleep(0.3)
                    if video_date and self.date_older_or_not(video_date.text) :                            
                            video_url = thumb.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            post_url = thumb.find_element(By.TAG_NAME, 'img').get_attribute('src')
                            if video_url and post_url and video_url not in df_url:
                                print(f'add video url in lists')
                                videos_urls.append({"video_url":video_url,'post_url':post_url})
                                if len(videos_urls) >= found_max_videos:
                                    break
            except Exception as e :
                print(e)

            if len(videos_urls) < found_max_videos :
                try:
                    next_page = self.find_element('ul',  "ul.eqrwdcp0.one-list-fhj8o6.e13hbd3c0", By.CSS_SELECTOR).find_elements(By.TAG_NAME, 'li')[-2].find_element(By.TAG_NAME, 'a')
                    if next_page: self.ensure_click(next_page)
                except:
                    break
                    
        video_detailes['video_list'] = videos_urls
        return video_detailes

    def download_brazzer_videos(self, videos_dict,Site_name=''):
        videos_urls = videos_dict['video_list']
        collection_name = videos_dict['collection_name']
        csv_name = collection_name if Site_name else self.brazzers.website_name

        if 'brazzers_main' in Site_name: 
            collection_path = self.create_or_check_path(Site_name)
            # sub_folder = Site_name

        elif Site_name:
            collection_path = self.create_or_check_path(collection_name.replace('brazzers_', ''))
            # sub_folder = collection_name.replace('brazzers_', '')

        else: 
            collection_path = self.create_or_check_path(self.brazzers_category_path)
            # sub_folder = None

        for idx, video_url in enumerate(videos_urls):
            self.driver.get(video_url['video_url'])
            self.random_sleep(10,15)
            video_name = f"{collection_name}_{self.sanitize_title(self.driver.current_url.split('https://site-ma.brazzers.com/')[-1])}"
            v_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
            p_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
            tmp = {
                    "Likes" : "",
                    "Disclike" :"",
                    "Url" : video_url['video_url'],
                    "Category" : collection_name,
                    "video_download_url" : v_url,
                    "Title" : '',
                    "Discription" : "",
                    "Release-Date" : "",
                    "Poster-Image_uri" : video_url['post_url'],
                    "poster_download_uri" : p_url,
                    "Video-name" : f'{video_name}.mp4',
                    "Photo-name" : f'{video_name}.jpg',
                    "Pornstarts" : '',
                    "Username" : self.brazzers.website_name,
                }
            try:
                likes_count = self.find_element('Likes count','//*[text()="Likes:"]/strong')
                if likes_count :
                    tmp['Likes'] = likes_count.text

                # self.getvalue_byscript('document.querySelector("#root > div.sc-yo7o1v-0.hlvViO > div.sc-yo7o1v-0.hlvViO > div.sc-1fep8qc-0.ekNhDD > div.sc-1deoyo3-0.iejyDN > div:nth-child(1) > div > section > div.sc-1wa37oa-0.irrdH > div.sc-bfcq3s-0.ePiyNl > div.sc-k44n71-0.gbGmcO > span:nth-child(1) > strong").textContent')
                Disclike_count = self.find_element('Disclike count','//*[text()="Dislikes:"]/strong')
                if Disclike_count :
                    tmp['Disclike'] = Disclike_count.text

                Title = self.find_element('Title','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[5]/div/section/div/div/h2[2]')
                if Title :
                    tmp['Title'] = Title.text

                Release = self.find_element('Release','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[5]/div/section/div/div/h2[1]')
                if Release :
                    tmp['Release-Date'] = Release.text

                Discription = self.find_element('Discription','/html/body/div[1]/div[1]/div[2]/div[3]/div[2]/div[6]/div/section/div/p')
                if Discription :
                    tmp['Discription'] = Discription.text

                port_starts = self.find_element('pornstars','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[5]/div/section/div/div/div[2]/h2')
                if port_starts :
                    tmp['Pornstarts'] = port_starts.text

                response = requests.get(video_url['post_url'])
                with open(f'{collection_path}/{video_name}.jpg', 'wb') as f:f.write(response.content)
                self.click_element('download btn', '//button[@class="sc-yox8zw-1 VZGJD sc-rco9ie-0 jnUyEX"]') 
                self.click_element('download high_quality','//div[@class="sc-yox8zw-0 cQnfGv"]/ul/div/button[1]')
                file_name = self.wait_for_file_download()
                self.random_sleep(3,5)
                name_of_file = os.path.join(self.download_path, f'{video_name}.mp4')
                os.rename(os.path.join(self.download_path,file_name), name_of_file)
                self.random_sleep(3,5)
                self.copy_files_in_catagory_folder(name_of_file,collection_path)
                self.set_data_of_csv(csv_name,tmp,video_name=video_name)
            except Exception as e:
                print('Error:', e)

    def wait_for_file_download(self,timeout=600,download_dir="downloads"):
        print('waiting for download')
        seconds = 0
        new_video_download = ''
        while seconds < timeout :
            time.sleep(1)
            new_video_download = [i for i in os.listdir(download_dir)if i.endswith('.crdownload')]
            if new_video_download:
                break
            else:
                seconds+=1
        if not new_video_download: return None
        while True:
            new_files = [i for i in os.listdir(download_dir)if i.endswith('.crdownload')]
            if not new_files:
                print('download complete')
                return  new_video_download[0].replace('.crdownload','').split('/')[-1]
            time.sleep(1)

    def create_or_check_path(self,folder_name, sub_folder_=None,main=False):
        folder_name = folder_name if not os.path.isdir(folder_name) else os.path.basename(folder_name)
        base_path = os.path.join(os.getcwd(), 'downloads') if not main else os.getcwd()
        folder = os.path.join(base_path, folder_name)
        if sub_folder_: folder = os.path.join(folder, sub_folder_)
        os.makedirs(folder, exist_ok=True)
        return folder
    
    def copy_files_in_catagory_folder(self,src_file,dst_folder):
        shutil.move(src_file, os.path.join(dst_folder, os.path.basename(src_file)))
        
    def make_csv(self,website_name : str = '',new :bool = False):
        if not new:
            for object in configuration.objects.all():
                website_name = object.website_name
                website_video_csv_path = os.path.join(self.csv_path,f'{website_name}_videos.csv')
                website_video_details_csv_path = os.path.join(self.csv_path,f'{website_name}_videos_details.csv')
                if not os.path.exists(website_video_csv_path) :
                    column_names = ["Video-title","video_url","downloaded_time"]
                    df = pd.DataFrame(columns=column_names)
                    df.to_csv(website_video_csv_path, index=False)

                if not os.path.exists(website_video_details_csv_path) :
                    column_names = ["Likes","Disclike","Url","Title","Discription","Release-Date","Poster-Image_uri",'poster_download_uri',"Video-name",'video_download_uri',"Photo-name","Pornstarts","Category","Username"]
                    df = pd.DataFrame(columns=column_names)
                    df.to_csv(website_video_details_csv_path, index=False)
                    
        if new and website_name:
            if '_videos' in website_name:website_name =website_name.replace('_videos','')
            website_video_csv_path = os.path.join(self.csv_path,f'{website_name}_videos.csv')
            website_video_details_csv_path = os.path.join(self.csv_path,f'{website_name}_videos_details.csv')
            if not os.path.exists(website_video_csv_path) :
                column_names = ["Video-title","video_url","downloaded_time"]
                df = pd.DataFrame(columns=column_names)
                df.to_csv(website_video_csv_path, index=False)

            if not os.path.exists(website_video_details_csv_path) :
                column_names = ["Likes","Disclike","Url","Title","Discription","Release-Date","Poster-Image_uri",'poster_download_uri',"Video-name",'video_download_uri',"Photo-name","Pornstarts","Category","Username"]
                df = pd.DataFrame(columns=column_names)
                df.to_csv(website_video_details_csv_path, index=False)

    def delete_old_videos(self):
        self.delete_resume_file()
        files = os.listdir(self.csv_path)
        base_name_dict = defaultdict(list)
        for file in files:
            base_name = file.split('_')[0]            
            base_name_dict[base_name].append(file)
        for base_name, file_list in base_name_dict.items():
            if len(file_list) == 1:
                os.remove(file_list[0])
                df = pd.read_csv(os.path.join(self.csv_path,file_list[1]))
                df['downloaded_time'] = pd.to_datetime(df['downloaded_time'])
                df1 = pd.read_csv(os.path.join(self.csv_path,file_list[0]))
                temp_df = df[df['downloaded_time'] < (datetime.now() - timedelta(days=int(object.delete_old_days)))]
                if not temp_df.empty:
                    matching_titles = temp_df['Video-title'].unique()
                    matching_url = temp_df['video_url'].unique()
                    if matching_titles:
                        for idx,row in temp_df.iterrows():
                            self.find_and_delete_video('downloads',row['Video-title'])
                        df1 = df1[~df1['video_download_url'].isin(matching_url)]
                        df1.to_csv(os.path.join(self.csv_path,file_list[0]),index=False)
        
    def delete_resume_file(self):
        delete_resume_file = [i for i in os.listdir('downloads')if i.endswith('.crdownload')]
        if delete_resume_file:
            for i in delete_resume_file:
                file_path = os.path.join(self.download_path, i)
                os.remove(file_path)
        base_name_dict = defaultdict(list)
        for foldername, subfolders, filenames in os.walk(os.path.join(os.getcwd(), 'downloads')):
            for filename in filenames:
                base_name = os.path.splitext(os.path.basename(filename))[0]
                if os.path.basename(filename).endswith('.mp4') or os.path.basename(filename).endswith('.jpg'):
                    base_name_dict[base_name].append(os.path.join(foldername, filename))
        for base_name, file_list in base_name_dict.items():
            if len(file_list) == 1:
                os.remove(file_list[0])


    def solve_2captcha(self,site_key, site_url):
        solver = TwoCaptcha('6e00098870d05c550b921b362c2abde8')
        response = solver.turnstile(sitekey=site_key,url=site_url,                             action='challenge',                            useragent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
        # captcha_url = "http://2captcha.com/in.php"
        # api_key = '6e00098870d05c550b921b362c2abde8'
        # captcha_payload = {'key': api_key, 'method': 'turnstile', 'googlekey': site_key, 'pageurl': site_url, "json": 1 }
        # response = requests.post(captcha_url, data=captcha_payload)
        if response:
            captcha = response['code']
            return captcha
        else:
            raise Exception("Error submitting CAPTCHA: " + response.text)
        
        # Step 2: Poll for the result
        # result_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
        # while True:
        #     result_response = requests.get(result_url)
        #     if result_response.text == 'CAPCHA_NOT_READY':
        #         time.sleep(5)  # wait before trying again
        #         continue
        #     if 'OK|' in result_response.text:
        #         captcha_result = result_response.text.split('|')[1]
        #         return captcha_result



    def vip4k_login(self):
        # self.CloseDriver()
        # self.driver = Driver(uc=True, headless=headless)
        for i in range(3):
            self.driver.get('https://www.nowsecure.nl')
            self.driver.get('https://vip4k.com/en/login')
            login = self.find_element('login button','//*[text()="Login"]')
            if login:
                self.load_cookies(self.vip4k.website_name)
                login = self.find_element('login button','//*[text()="Login"]')
                if login:
                    self.click_element('login button','//*[text()="Login"]')
                    self.random_sleep(2,4)
                    self.input_text(self.vip4k.username,'username','login-username',By.ID)
                    self.random_sleep(2,3)
                    self.input_text(self.vip4k.password,'password','login-password',By.ID)
                    self.random_sleep(2,3)
                    site_key_ele = self.find_element('SITE-KEY','g-recaptcha',By.CLASS_NAME)
                    if site_key_ele:
                        solver = recaptchaV2Proxyless()
                        solver.set_verbose(1)
                        solver.set_key("e49c2cc94651faab912d635baec6741f")    
                    #     # to solvee the captcha
                        site_key = site_key_ele.get_attribute('data-sitekey')
                        g_response = self.solve_2captcha(site_key=site_key, site_url=self.driver.current_url)
                        self.driver.execute_script(f'''var els=document.getElementsByName("g-recaptcha-response");for (var i=0;i<els.length;i++) {{els[i].value = "{g_response}";}}''')

                    #     solver.set_website_url(self.driver.current_url)
                    #     solver.set_website_key(site_key)
                    #     solver.set_soft_id(0)
                    #     g_response = solver.solve_and_return_solution()
                        
                    #     if g_response == 0:
                    #         print ("task finished of captcha solver with error "+solver.error_code)
                    #         return False
                    #     print ("g-response: "+g_response)
                        # self.driver.execute_script(f'document.querySelector("#cf-chl-widget-65aqx_g_response").value="{g_response}";')
                        # self.driver.execute_script(f'document.querySelector("#cf-chl-widget-ixf9o_g_response").value="{g_response}";')
                        # aa  = self.find_element('response', 'g-recaptcha-response', By.NAME)
                        # self.driver.execute_script(f'document.getElementsByName("g-recaptcha-response").value = "{g_response}";')
                    # iframe = WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, f'//iframe[@title="reCAPTCHA"]')))
                    # self.driver.execute_script('document.querySelector("#recaptcha-token").click()')
                    # self.driver.switch_to.default_content()
                    # self.random_sleep(2,3)
                    # iframe = WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, f'//iframe[@title="recaptcha challenge expires in two minutes"]')))        
                    # self.click_element('click extension btn','//*[@id="rc-imageselect"]/div[3]/div[2]/div[1]/div[1]/div[4]')
                    
                    # self.driver.switch_to.default_content()
                    
                    # self.random_sleep(10,15)
                    self.click_element('submit','//input[@type="submit"]')
                    self.random_sleep(5,6)
            if self.find_element('check login','//div[@class="logout__text"]'):
                cookies = self.get_cookies(self.vip4k.website_name)
                # member_cookies = [item for item in cookies if item.get("domain") != ".vip4k.com"]
                # for item in member_cookies:self.driver.add_cookie(item)
                # self.driver.quit()
                # self.get_driver()
                # self.driver.get('https://vip4k.com/en/login')
                # self.load_cookies(self.vip4k.website_name)
                return True
            
    def download_all_vip_channels_video(self):
        self.driver.get('https://members.vip4k.com/en/channels')
        all_li = self.driver.find_elements(By.XPATH, '//li[@class="grid__item"]')
        if all_li:
            all_channel_url = [li.find_element(By.TAG_NAME, 'a').get_attribute('href') for li in all_li]
            for channel in all_channel_url:
                video_dict = self.vip4k_get_video(channel, True)
                self.vip4k_download_video(video_dict)

        
    def vip4k_get_video(self,url :str='', channel: bool= False):
        self.calculate_old_date(self.vip4k.more_than_old_days_download)
        video_detailes = {'collection_name':'','video_list':[]}
        videos_urls = []
        if channel: self.driver.get(url)
        else:self.driver.get(f'https://members.vip4k.com/en/tag/{self.vip4k.category}')
        self.random_sleep(10,15)
        collection_name = self.find_element('collection name','//h1[@class="section__title title title--sm"]', timeout=5)
        if not collection_name: collection_name = self.find_element('collection name','//h1')
        video_detailes['collection_name'] = collection_name.text.lower().replace(' ','_')
        new_csv= True if '4k' in video_detailes['collection_name'] or 'sis_videos' in video_detailes['collection_name'] else False
        website_name = f"vip4k_{video_detailes['collection_name']}" if new_csv else self.vip4k.website_name
        self.make_csv(website_name, new=new_csv)
        # if new_csv:
        df_url = self.column_to_list(self.vip4k.website_name,'Url')
        max_video = self.vip4k.numbers_of_download_videos
        while len(videos_urls) < max_video:
            ul_tag = self.find_element('ul tag', 'grid.sets_grid', By.CLASS_NAME)
            li_tags = ul_tag.find_elements(By.TAG_NAME, 'li')
            for li in li_tags:
                video_date = li.find_element(By.CLASS_NAME, 'item__date').text
                if video_date and self.date_older_or_not(video_date):
                    video_url = li.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    post_url = li.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    if video_url and not post_url: 
                        self.random_sleep(5,7)
                        post_url = li.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    if video_url and post_url:
                        if video_url not in df_url and video_url not in [item['video_url'] for item in videos_urls]:
                            videos_urls.append({"video_url": video_url, 'post_url': post_url})
                            if len(videos_urls) >= max_video:break
                    if len(videos_urls) >= max_video:break
            if len(videos_urls) >= max_video:break
            show_more = self.find_element('show more','/html/body/div[2]/div/div[1]/div/section/div[5]/a')
            if show_more:
                self.driver.execute_script("arguments[0].scrollIntoView();", show_more)
                show_more.click()
            else:
                break
        video_detailes['video_list'] = videos_urls
        return video_detailes

    def sanitize_title(self,title : str):
        formatted_title = ''.join(c.lower() if c.isalnum() else '_' for c in title)
        formatted_title = '_'.join(filter(None, formatted_title.split('_')))
        return formatted_title
    
    def download_video_from_request(self, url, filename, headers = None):
        if headers:
            response = requests.get(url, headers=headers ,stream=True)
        else: 
            response = requests.get(url, stream=True)
        
        # Total size in bytes, may be None if content-length header is not set
        total_size = int(response.headers.get('content-length', 0))
        
        # Open a local file for writing the binary stream
        with open(filename, 'wb') as f, tqdm(
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)

    def vip4k_download_video(self,videos_dict : dict):
        videos_urls = videos_dict['video_list']
        collection_name = videos_dict['collection_name']
        collection_path = self.create_or_check_path(self.vip4k_category_path,sub_folder_=collection_name)
        new_csv= True if '4k' in collection_name or 'sis_videos' in collection_name else False
        website_name = f'vip4k_{collection_name}' if new_csv else self.vip4k.website_name

        for idx, video_url in enumerate(videos_urls):
            self.driver.get(video_url['video_url'])
            # self.find_element()
            self.random_sleep(10,15)
            tmp = {
                    "Likes" : "",
                    "Disclike" :"",
                    "Url" : video_url['video_url'],
                    "Category" : videos_dict['collection_name'],
                    "video_download_url" : '',
                    "Title" : '',
                    "Discription" : "",
                    "Release-Date" : "",
                    "Poster-Image_uri" : video_url['post_url'],
                    "poster_download_uri" : '',
                    "Video-name" : '',
                    "Photo-name" : '',
                    "Pornstarts" : '',
                    "Username" : self.vip4k.website_name,
                }
            try:
                likes_count = self.find_element('Likes count','//button[@class="player-vote__item player-vote__item--up "]')
                if likes_count :
                    tmp['Likes'] = likes_count.text

                # self.getvalue_byscript('document.querySelector("#root > div.sc-yo7o1v-0.hlvViO > div.sc-yo7o1v-0.hlvViO > div.sc-1fep8qc-0.ekNhDD > div.sc-1deoyo3-0.iejyDN > div:nth-child(1) > div > section > div.sc-1wa37oa-0.irrdH > div.sc-bfcq3s-0.ePiyNl > div.sc-k44n71-0.gbGmcO > span:nth-child(1) > strong").textContent')
                Disclike_count = self.find_element('Disclike count','//button[@class="player-vote__item player-vote__item--down "]')
                if Disclike_count :
                    tmp['Disclike'] = Disclike_count.text

                Title = self.find_element('Title','//h1[@class="player-description__title"]')
                if Title :
                    tmp['Title'] = Title.text

                Release = self.find_element('Release',"//li[@class='player-additional__item'][2]")
                if Release :
                    tmp['Release-Date'] = Release.text

                Discription = self.find_element('Discription','//div[@class="player-description__text"]')
                if Discription :
                    tmp['Discription'] = Discription.text

                porn_starts = self.driver.find_elements(By.XPATH,'//div[@class="model__name"]')
                if porn_starts:
                    porn_start_name = ''
                    for i in porn_starts:
                        porn_start_name += f'{i.text},'
                    tmp['Pornstarts'] = porn_start_name.rstrip(',')
                video_name = f"vip4k_{collection_name.replace('_videos', '')}_{self.sanitize_title(tmp['Title'])}"

                v_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
                p_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
                tmp['poster_download_uri'] = p_url
                tmp['video_download_url'] = v_url
                tmp['Photo-name'] = f'{video_name}.jpg'
                tmp['Video-name'] = f'{video_name}.mp4'
                response = requests.get(video_url['post_url'])
                with open(f'{collection_path}/{video_name}.jpg', 'wb') as f:f.write(response.content)
                local_filename =  os.path.join(collection_path, f'{video_name}.mp4')
                FullHD_link = self.driver.find_element(By.XPATH, '//a[contains(@download, "FullHD.mp4")]').get_attribute('data-download')
                if FullHD_link:
                    self.driver.get(f'https://members.vip4k.com{FullHD_link}')
                    self.random_sleep(2,3)
                    page_source = self.driver.page_source
                    start = page_source.find('<pre>') + 5
                    end = page_source.find('</pre>', start)
                    json_data = page_source[start:end]
                    data = json.loads(json_data)
                    decoded_url = unquote(data['url']).replace('\\/', '/')
                    self.download_video_from_request(decoded_url, local_filename)
                else:continue

                # js_script = """
                #     var downloadLinks = document.querySelectorAll('.download__item');
                #     for (var i = 0; i < downloadLinks.length; i++) {
                #         var link = downloadLinks[i];
                #         if (link.getAttribute('download').includes('FullHD.mp4')) {
                #             link.click();
                #             break;
                #         }
                #     }
                #     """
                # self.driver.execute_script(js_script)
                # file_name = self.wait_for_file_download(timeout=30)
                # if not file_name: 
                #     print('file downloading not started')
                #     continue
                # self.random_sleep(3,5)
                # name_of_file = os.path.join(self.download_path, f'{video_name}.mp4')
                # os.rename(os.path.join(self.download_path,file_name), name_of_file)
                # self.copy_files_in_catagory_folder(name_of_file,collection_path)
                self.set_data_of_csv(website_name,tmp,video_name)
            except Exception as e:
                print('Error:', e)




    def login_Handjob_TV(self):
        url = "https://handjob.tv/login"
        self.driver.get(url)
        self.click_element('agree btn','verify-age', By.ID)
        self.input_text(self.handjob.username,'username','//input[@id="username"]')
        self.input_text(self.handjob.password,'password','//input[@id="password"]')
        self.click_element('Submit btn','//button[@id="login"]')
        self.input_text(self.handjob.category,'password','//input[@id="search"]')
        # self.driver.get(f'https://handjob.tv/search/{self.handjob.category}/')
        if self.find_element('Logout btn','//a[@class="logout"]') :
            self.get_cookies(self.handjob.website_name)
            return True
        else : return False
        
        
        self.cookies_dict = ''
        cookies_file = f'{self.cookies_path}/{self.handjob.website_name}_cookietest.json'
        if os.path.isfile(cookies_file):
            with open(cookies_file, 'r') as file: 
                self.cookies_dict = json.load(file)
            response = requests.request("GET", url, cookies=self.cookies_dict)
            soup = BeautifulSoup(response.content, 'html.parser')
            logout = soup.find('a', class_="logout")
            if logout:
                return True
            
        headers = {'Cookies':'_ga=GA1.1.1004529152.1702469470; PHPSESSID=rugc1hlu0itorhumpom12pk59q; _ga_HK7FVQ1HVZ=GS1.1.1702982456.7.1.1702982470.0.0.0'}
        response = requests.request("GET", url, headers=headers)
        hidden_input = soup.find('input', {'name': 'nocsrf_login_popup'})
        if hidden_input:
            value = hidden_input.get('value')
            payload = {'u': 'romeostream', 'p' : 'tub3S3bm1t', 'nocsrf_login_popup' : f'{value}'}
            print('value found')
        else:
            payload = {'u': 'romeostream', 'p' : 'tub3S3bm1t'}

        url = "https://handjob.tv/api/verifying"
        headers =   {
                        'Content-Type' :  'application/x-www-form-urlencoded'
                    }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            self.cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
            with open(cookies_file, 'w') as file:
                json.dump(self.cookies_dict, file)
            print("Cookies saved to cookies.json file.")
            soup = BeautifulSoup(response.content, 'html.parser')
            logout = soup.find('a', class_="logout")
            if logout:
                return True
        return False


    def genrate_handjob_a_data_dict(self,video_li : list,hand_job_category_name : str):
        
        video_info = self.find_element('Video0info','video-info',By.CLASS_NAME)
        vd_title = self.find_element('Video title','video-title',By.CLASS_NAME).text if self.find_element('Video title','video-title',By.CLASS_NAME) else None

        video_name = f"{self.handjob.website_name}_{hand_job_category_name}_{self.sanitize_title(vd_title)}"
        data = {       
        "Likes" : "Not available",
        "Disclike" : "Not available",
        "Url" : self.driver.current_url,
        "Title" : self.find_element('Video title','video-title',By.CLASS_NAME).text if self.find_element('Video title','video-title',By.CLASS_NAME) else "could not found the title" ,
        "Discription" : self.find_element('Video title','//div[@style="color: white;"]',By.XPATH).text if self.find_element('Video title','//div[@style="color: white;"]',By.XPATH) else "could not found the description" , #color: white;
        "Release-Date" : video_info.find_element(By.TAG_NAME,'div').find_elements(By.TAG_NAME,'p')[-1].text.removeprefix('Added on: ') if video_info else "could not found the added date time", #/html/body/div[4]/div[1]/div
        "Poster-Image_uri" : video_li[-1] if video_li[-1] else "video post img link could not found",
        "poster_download_uri" : f'http://208.122.217.49:8000/downloads/handjob_category_videos/{hand_job_category_name}/{video_name}.jpg',
        "Video-name" : video_name+".mp4",
        "video_download_url" : f'http://208.122.217.49:8000/downloads/handjob_category_videos/{hand_job_category_name}/{video_name}.mp4',
        "Photo-name" : video_name + ".jpg",
        "Pornstarts" : self.find_element('Pornstar name','model-tags',By.CLASS_NAME).text.replace("Model: ",'') if self.find_element('Pornstar name','model-tags',By.CLASS_NAME) else "Not found porn star",
        "Category" : hand_job_category_name,
        "Username" : self.handjob.username,
        "downloaded_time" : datetime.now()
        }
                
        return data
    
    def other_sites_of_handjob(self):
        other_sites_cetegory = [
            "https://handjob.tv/videos/strokies/",
            "https://handjob.tv/videos/tugcasting/",
            "https://handjob.tv/videos/publichandjobs/",
            "https://handjob.tv/videos/strictlyhands/"
            ]
        
        
        
        for link in other_sites_cetegory: 
            handjob_not_used_links = []
            hand_job_category_name = link.split('https://handjob.tv/videos/')[-1].replace('/','')
            details_csv_path = 'handjob_'+link.split('https://handjob.tv/videos/')[-1].replace('/','')
            # details_csv_path = os.path.join(os.getcwd(),'csv',details_csv_path)
            # check_csv_with_columns(details_csv_path)
            self.make_csv(details_csv_path, new=True)
            
            
            self.driver.get(link)
            find_last_pag_num = 0
            
            last_page_ele = self.driver.find_elements(By.XPATH,'//*[@id="pagination"]/div/*')[-1]
            if last_page_ele.find_elements(By.TAG_NAME,'a'):
                find_last_pag_num = last_page_ele.find_elements(By.TAG_NAME,'a')[0].get_attribute('href').split('/')[-1].replace('page','')
            
            if not find_last_pag_num :
                print("cound not found the find_last_pag_num for hand job other sites of category")
                continue

            all_used_link = self.column_to_list(details_csv_path,'Url')
            
            for pages in range(int(find_last_pag_num)): 
                
                if pages == 0:
                    self.driver.get(link)
                else:
                    self.driver.get(link+'page'+str(pages))
                    
                all_videos_thumbs = self.driver.find_elements(By.CLASS_NAME,'thumb-all')
                for i in all_videos_thumbs : 
                    vd_link = i.find_element(By.TAG_NAME,'a').get_attribute('href')
                    if not vd_link in all_used_link :
                        handjob_not_used_links.append([vd_link,i.find_element(By.TAG_NAME,'img').get_attribute('src')])
                        
                    if len(handjob_not_used_links) > self.handjob.numbers_of_download_videos : break
                if len(handjob_not_used_links) > self.handjob.numbers_of_download_videos : break
            
            for vd_link in handjob_not_used_links:

                self.driver.get(vd_link[0])
                self.random_sleep(10,15)

                self.driver.find_elements(By.XPATH,'//*[@class="download-full-movie"]/div/*')[-2].click()
                self.random_sleep(3,5)

                file_name = self.wait_for_file_download()
                self.random_sleep(3,5)

                video_infor = self.genrate_handjob_a_data_dict(vd_link,hand_job_category_name)
                name_of_file = os.path.join(self.download_path, video_infor['Video-name'])

                os.rename(os.path.join(self.download_path,file_name), name_of_file)
                self.random_sleep(3,5)
                
                collection_path = os.path.join(self.download_path,f'handjon_{hand_job_category_name}')
                if not os.path.exists(collection_path):
                    os.mkdir(collection_path)
                
                response = requests.get(vd_link[1])
                if response.status_code == 200:
                    with open(f'{collection_path}/{video_infor["Video-name"]}.jpg', 'wb') as file:
                        file.write(response.content)

                shutil.move(name_of_file,os.path.join(self.download_path,f'handjon_{hand_job_category_name}',video_infor['Video-name']))
                self.set_data_of_csv( 'handjob_'+link.split('https://handjob.tv/videos/')[-1].replace('/',''),video_infor, video_infor["Video-name"])
            
                
                
    def handjob_get_video(self,url=None):
        videos_urls = []
        VideosNumberDone = 0
        # self.other_sites_of_handjob()
        self.driver.page_source
        self.driver.get(f'https://handjob.tv/search/{self.handjob.category}/')
        df_url = self.column_to_list(self.handjob.website_name,'Url')
        self.calculate_old_date(self.handjob.more_than_old_days_download)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        collection_path = self.create_or_check_path(self.handjob_category_path,sub_folder_=self.handjob.category)
        found_max_videos = self.handjob.numbers_of_download_videos
        # all_thimb = soup.find_all('div', class_='thumb-all')
        # video_links = soup.find_all('a', href=lambda value: value and '/video/' in value)
        video_links = soup.find_all('a', href=lambda value: value and '/video/' in value)
        
               
        
        for link in video_links:
            video_url = link['href']
            
            img_tag = link.find('img', alt='', src=True)
            if not img_tag or not video_url : continue
            
            video_date_ele = link.select_one('span.bio-videos-date')
            if not video_date_ele : continue
            
            date_string = video_date_ele.get_text(strip=True)
            if not self.date_older_or_not(date_string) : continue

            video_url = 'https://handjob.tv' + video_url
            img_src = 'https:'+img_tag['src']
            if video_url in df_url : continue
            print("Video URL:", video_url)
            print("Image Source:", img_src)
            self.driver.get(video_url)
            
            video_ele = self.find_element('Video Link','video',By.TAG_NAME)
            video_title_ele = self.find_element('Video Title','h1',By.TAG_NAME)
            if not video_ele or not video_title_ele: continue
            
            video_title = video_title_ele.text
            
            # video_link = video_ele.get_attribute('src')
            video_link = self.driver.find_elements(By.XPATH,'//*[@class="download-full-movie"]/div/*')[-2].get_attribute('href')
            video_name = f"handjob_{self.handjob.category.replace('videos', '')}_{self.sanitize_title(video_title)}"
            
            VideoDdownloaded = False
            try :VideoDdownloaded = urllib.request.urlretrieve(video_link, os.path.join(collection_path, f'{video_name}.mp4'))
            except Exception as e : print('Error : Videos downloading in handjob :',e)
            
            try :ImgDownloaded = urllib.request.urlretrieve(img_src, os.path.join(collection_path, f'{video_name}.jpg'))
            except Exception as e : print('Error : image downloading in handjob :',e)
            if not VideoDdownloaded or not ImgDownloaded : 
                print('error : Video or Image could not download in hand job')
                continue
            
            tmp = {"Likes" : "","Disclike" :"","Url" : video_url,"Category" : self.handjob.category,"video_download_url" : '',"Title" : '',"Discription" : "","Release-Date" : "","Poster-Image_uri" : img_src,"poster_download_uri" : '',"Video-name" : '',"Photo-name" : '',"Pornstarts" : '',"Username" : self.handjob.website_name}
            
            model_name_ele = self.find_element('models name','//div[@class="model-tags"]')
            if model_name_ele :
                model_name = model_name_ele.text.replace('Model:','').strip()
            else : model_name

            
            v_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'
            p_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'
            
            discription = ''
            All_Ptag = self.driver.find_elements(By.TAG_NAME,'p')
            for Ptag in All_Ptag : 
                PtagText = Ptag.text.strip()
                if not PtagText or PtagText.startswith('Lenght') or PtagText.startswith('Photos') or  PtagText.startswith('Added on: '):continue
                discription += PtagText
                
            tmp['Title'] = video_title
            tmp['Discription'] = discription
            tmp['Release-Date'] = date_string
            tmp['Video-name'] = f'{video_name}.mp4'
            tmp['Photo-name'] = f'{video_name}.jpg'
            tmp['poster_download_uri'] = p_url
            tmp['video_download_url'] = v_url
            tmp['Pornstarts'] = model_name                             
            self.set_data_of_csv(self.handjob.website_name,tmp,video_name)
            
            VideosNumberDone += 1
            if VideosNumberDone >= found_max_videos :return
            
            # 
        # for i in all_thimb:
            # video_url = 'https://handjob.tv'+link.find('a').get('href')
            # post_url = i.find('img').get('src')
            # if video_url and post_url and video_url not in df_url:
            #     self.driver.get(video_url)
            #     soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            #     paragraphs = soup.find_all('p')
            #     date_element = next((p for p in paragraphs if 'Added on' in p.get_text()), None)

            #     if date_element:
            #         date = date_element.get_text(strip=True).split(': ')[1]
            #         if date and self.date_older_or_not(date) :
            #             tmp = {
            #                     "Likes" : "",
            #                     "Disclike" :"",
            #                     "Url" : video_url,
            #                     "Category" : self.handjob.category,
            #                     "video_download_url" : '',
            #                     "Title" : '',
            #                     "Discription" : "",
            #                     "Release-Date" : "",
            #                     "Poster-Image_uri" : post_url,
            #                     "poster_download_uri" : '',
            #                     "Video-name" : '',
            #                     "Photo-name" : '',
            #                     "Pornstarts" : '',
            #                     "Username" : self.handjob.website_name,
            #                 }
            #             video_title = soup.find('h1', class_='video-title').get_text(strip=True)
            #             video_name = f"handjob_{self.handjob.category.replace('videos', '')}_{video_title.lower().replace(' ', '_')}"
            #             v_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'
            #             p_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'
            #             model_tags_div = soup.find('div', class_='model-tags')
            #             if model_tags_div:
            #                 model_name_element = model_tags_div.find('a')
            #                 if model_name_element:
            #                     model_name = model_name_element.get_text(strip=True)
            #                     tmp['Pornstarts'] = model_name                             
                        
            #             video_link = soup.find('a', text='1080p').get('href')
            #             discribe = soup.find('div', class_='video-text')
            #             discription = ''
            #             for i in discribe.find_all('p')[3:]:
            #                 discription +=i.get_text(strip=True)
            #             tmp['Title'] = video_title
            #             tmp['Discription'] = discription
            #             tmp['Release-Date'] = date
            #             tmp['Video-name'] = f'{video_name}.mp4'
            #             tmp['Photo-name'] = f'{video_name}.jpg'
            #             tmp['poster_download_uri'] = p_url
            #             tmp['video_download_url'] = v_url
            #             
            #             response = requests.request("GET", video_link)
            #             if response.status_code == 200:
            #                 with open(f'{collection_path}/{video_name}.mp4', 'wb') as file:
            #                     file.write(response.content)
            #             response = requests.request("GET", post_url)
            #             if response.status_code == 200:
            #                 with open(f'{collection_path}/{video_name}.jpg', 'wb') as file:file.write(response.content)
            #             self.set_data_of_csv(self.handjob.website_name,tmp,video_name)
            #     videos_urls.append({"video_url":video_url,'post_url':post_url})
            #     if len(videos_urls) >= found_max_videos :return

    def Sovle_captcha(self):
        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key("e49c2cc94651faab912d635baec6741f")
        site_key_ele = self.find_element('SITE-KEY','g-recaptcha',By.CLASS_NAME)
        
        if site_key_ele : 
            # to solvee the captcha
            site_key = site_key_ele.get_attribute('data-sitekey')
            solver.set_website_url(self.driver.current_url)
            solver.set_website_key(site_key)
            solver.set_soft_id(0)
            g_response = solver.solve_and_return_solution()
            
            if g_response == 0:
                print ("task finished of captcha solver with error "+solver.error_code)
                return False
            print ("g-response: "+g_response)
            self.driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML = "{g_response}";')
            
            # captcha_text_area_id = 'g-recaptcha-response'
            # captcha_response = self.find_element('Captcha-text-area',captcha_text_area_id,By.ID,timeout=3)
            # if not captcha_response :
            #     captcha_text_area_id = 'g-recaptcha-response-1'
            #     captcha_response = self.find_element('captcha 2 text area',captcha_text_area_id,By.ID,timeout=3)
            
            # if not captcha_response : return False
            # self.driver.execute_script("arguments[0].style.display = 'block';", captcha_response)
            # captcha_response = self.driver.find_element(By.ID, captcha_text_area_id)
            # captcha_response.send_keys(g_response)
            
            if g_response : return True
            
        return False

    
    def naughty_ame_login(self):
        # self.click_element('Login','//a[text()="LOGIN"]')
        # self.random_sleep(10,15)
        self.get_driver()
        self.driver.get('https://members.naughtyamerica.com/postLogin')
        self.load_cookies(self.naughty.website_name)
        self.driver.refresh()
        # self.random_sleep(10,15)
        if self.find_element('user btn','//*[@id="right-side-containter"]/div/div[2]/a/i') : 
            return True
        for i in range(3):
            self.input_text(self.naughty.username,'Username','//*[@id="login-top"]/input[1]')
            self.input_text(self.naughty.password,'Password','//*[@id="login-top"]/input[2]')
            # self.click_element('Login','//a[text()="LOGIN"]')
            self.Sovle_captcha()
            self.click_element('Login','login', By.ID)
            account_pause = self.find_element('account pause', '//*[contains(text(),"Account Paused. ")]')
            if account_pause:
                SendAnEmail('\n Your Naughty America account is Pause. \nPlease Check that.', email=self.emailss)
                return False
            self.random_sleep(10,15)
            self.driver.refresh()

            if self.find_element('Logout btn','//*[text()="Logout"]'):
                self.get_cookies(self.naughty.website_name)
                # member_cookies = [item for item in cookies if item.get("domain") == ".naughtyamerica.com"]
                # for item in member_cookies:self.driver.add_cookie(item)
                return True
        
        return False
       
    def Open_new_tab_with_link(self,link): 
        self.driver.execute_script(f"window.open('{link}')")
        
    def get_naughty_video_links(self):
        downloaded_vd_url = self.column_to_list(self.naughty.website_name,'Url')
        all_videos_link_li = []
        for _ in range(100):
                
            all_videos = self.driver.find_elements(By.XPATH, '//*[@style="cursor: pointer"]')
            for videos in all_videos:
                url__ = videos.get_attribute('href')
                
                if url__ not in downloaded_vd_url:continue
                all_videos_link_li.append(url__)
        
                if len(all_videos_link_li) >= self.naughty.numbers_of_download_videos :
                    return all_videos_link_li

            
            if not self.click_element('View more','view-all-button',By.CLASS_NAME):
                SendAnEmail('Could not find more videos into naughty america cetegories!',email=self.emailss)
                return
            
            self.random_sleep(10,15)
        return all_videos_link_li
        
    def naughty_video_download(self):
        """This functions helps to download the video at his place and save the details which is needed to save in csv"""
        collection_path = self.create_or_check_path(self.naughty_america_category_path)
        
        # click on more info
        self.click_element('more info','more-info',By.ID)
        
        # get and store the video details in dict
        data_dict = {}
        data_dict['Likes'] = ""
        data_dict['Disclike'] = ""
        data_dict['Url'] = self.driver.current_url
        data_dict['Category'] = self.naughty.category
        data_dict['video_download_url'] = self.naughty.category
        
        pornstar_ele = self.find_element('porn star','//*[@id="more-info-container"]/div[1]/p[2]')
        data_dict['Pornstarts'] = ""
        if not pornstar_ele : SendAnEmail('Could not find pornstars into naughty america!',email=self.emailss)
        else : data_dict['Pornstarts'] = pornstar_ele.text
        
        data_dict['Title'] = ""
        vd_title_ele = self.find_element('title','//p[@class="new-title"]')
        if not vd_title_ele : SendAnEmail('Could not find pornstars into naughty america!',email=self.emailss)
        else : data_dict['Title'] = vd_title_ele.text
        
        post_url = self.find_element('img', "//*[@class='play_image darken-image']").get_attribute('src')
        if post_url:
            data_dict['post_url'] = post_url

        
        video_name = f"naughty_{self.naughty.category.replace('videos', '')}_{self.sanitize_title(data_dict['Title'])}"
        data_dict['Video-name'] = f'{video_name}.mp4'
        data_dict['Photo-name'] = f'{video_name}.jpg'

        v_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'
        p_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'

        data_dict['video_download_url'] = v_url
        data_dict['poster_download_uri'] = p_url

        response = requests.get(post_url)
        with open(os.path.join(collection_path, f'{video_name}.jpg'), 'wb') as f:f.write(response.content)


        data_dict['Release-Date'] = ""
        script_content = self.driver.page_source
        vd_Release_ele = re.search(r"published_at: '(.*?)'", script_content)

        if not vd_Release_ele : SendAnEmail('Could not find pornstars into naughty america!',email=self.emailss)
        else : data_dict['Release-Date'] =  parser.parse(vd_Release_ele.group(1)).date().strftime('%Y-%m-%d')
        
        
        data_dict['Discription'] = ""
        vd_Discription_ele = self.find_element('Discription','//*[@id="more-info-container"]/div[1]/p[6]')
        if not vd_Discription_ele : SendAnEmail('Could not find description into naughty america!',email=self.emailss)
        else : data_dict['Discription'] = vd_Discription_ele.text
        
        
        self.click_element('4k download btn','//*[@id="download-options-menu"]/table/tbody/tr[3]/td[2]/a')
        self.Sovle_captcha()

        self.random_sleep(7,10)
        self.driver.switch_to.frame(self.find_element('iframe', '//*[@title="reCAPTCHA"]'))
        self.click_element('captcha', '//*[@class="recaptcha-checkbox-border"]')
        self.driver.switch_to.default_content()
        
        self.click_element('download btn', '//*[@type="submit"]')
        file_name = self.wait_for_file_download()
        self.random_sleep(3,5)
        name_of_file = os.path.join(self.download_path, f'{video_name}.mp4')
        os.rename(os.path.join(self.download_path,file_name), name_of_file)
        self.random_sleep(3,5)
        self.copy_files_in_catagory_folder(name_of_file,collection_path)
        self.set_data_of_csv(self.naughty.website_name,data_dict,video_name)
        return True
        
    def naughty_ame(self):
        try:
            if not self.find_element('categories','//*[@id="header-tags"]'):
                SendAnEmail('Could not find cetegories into naughty america!',email=self.emailss)
                return
            
            self.random_sleep()
            categories = []
            for _ in range(3) :
                categories = self.driver.find_element(By.ID,"header-tags").find_elements(By.TAG_NAME, 'a')
                if len(categories) > 5 : 
                    print('categories found')
                    break
                self.random_sleep()
            
            for cat in categories :
                self.driver.execute_script('arguments[0].scrollIntoViewIfNeeded();',cat)
                if cat.text.lower() == self.naughty.category.lower():
                    category_url = cat.get_attribute('href')
                    self.driver.get(category_url)
                    break

            # pagignation and video download conditions
            downloaded_vd_url = self.column_to_list(self.naughty.website_name,'Url')
            all_videos_link_li = 0
            for _ in range(100):
                all_videos = [video.get_attribute('href') for video in self.driver.find_elements(By.XPATH, '//*[@style="cursor: pointer"]')]
                print(f'{len(all_videos)} videos found')
                for url__ in all_videos:
                    if url__ in downloaded_vd_url:continue
                    self.driver.get(url__)
                    if self.find_element('subscribe', '//*[@class="unlock-button-small"]', timeout=3):
                        continue
                    self.naughty_video_download()
                    all_videos_link_li+= 1
                    if len(all_videos_link_li) >= self.naughty.numbers_of_download_videos :
                        return True

                
                if not self.click_element('View more','view-all-button',By.CLASS_NAME):
                    SendAnEmail('Could not find more videos into naughty america cetegories!',email=self.emailss)
                    return
                
                self.random_sleep(10,15)
        except Exception as e :
                SendAnEmail('Could not complete the naughty america scrapping!'+f'\n{e}',email=self.emailss)
    
    def adultprime_login(self):
        '''
        This function automates the login process for the AdultPrime website.

        Returns:
            bool: True if login is successful, False otherwise.
        '''

        # Captcha configuration
        solver = imagecaptcha()
        solver.set_verbose(1)
        solver.set_key("e49c2cc94651faab912d635baec6741f")
        solver.set_soft_id(0)

        # Configurations
        self.adultprime = configuration.objects.get(website_name='adultprime')
        self.adultprime_category_path = self.create_or_check_path('adultprime_category_videos')

        # Login process
        # self.driver = Driver(uc=True, headless=headless)
        self.get_driver()
        for i in range(2):
            self.driver.get('https://adultprime.com/')
            self.load_cookies(self.adultprime.website_name)
            if self.find_element('Sign Out', '//*[text()="Sign Out"]'):
                return True

            self.driver.save_screenshot('driver.png')
            self.click_element('confirm', "confirm-btn", By.ID)
            self.click_element('login btn', '//*[@class="login-menu-btn"]')
            self.input_text(self.adultprime.username, 'username_input', '//*[@id="login-form-main"]//*[@id="LoginForm_username"]')
            self.input_text(self.adultprime.password, 'password_input','//*[@id="login-form-main"]//*[@id="LoginForm_password"]')

            for i in range(3):
                self.click_element('refresh captcha', '//*[@id="yw0_button"]')
                self.random_sleep(1,2)
                captcha_link = self.find_element('links','//*[@id="yw0"]').get_attribute('src')
                self.driver.switch_to.new_window('tab')
                tabs = self.driver.window_handles
                self.driver.switch_to.window(tabs[-1])
                self.driver.get(captcha_link)
                img = self.find_element('img', 'img', By.TAG_NAME)
                captcha = img.screenshot_as_png
                self.random_sleep(2,3)
                self.driver.switch_to.window(tabs[0])
                with open('captcha.png', 'wb') as file:
                    file.write(captcha)
                captcha_text = solver.solve_and_return_solution('captcha.png')
                if captcha_text != 0:
                    self.input_text(captcha_text, 'captcha_input','//*[@id="login-form-main"]//*[@id="LoginForm_verifyCode"]', timeout=5)
                    print("captcha text :"+captcha_text)
                    os.remove('captcha.png')
                    self.click_element('login_btn','//*[@value="Login"]')
                    if self.find_element('Sign Out', '//*[text()="Sign Out"]'):
                        self.get_cookies(self.adultprime.website_name)
                        return True
                    if self.find_element('ip change', '//*[text()="Ip Change Detected"]'):
                        return False
                else:
                    self.click_element('refresh captcha', '//*[@id="yw0_button"]')
                    print("task finished with error "+solver.error_code)
        return False
    
    def get_adultprime_category(self):
        self.driver.get('https://adultprime.com/categories')
        self.random_sleep(2,3)
        while True:    
            all_a_tags = self.driver.find_elements(By.CLASS_NAME, "studio-link")
            for i in all_a_tags:
                if self.adultprime.category.lower() in i.text.lower():
                    self.ensure_click(i)
                    self.random_sleep(2,3)
                    if self.driver.current_url != 'https://adultprime.com/categories':
                        link_element = self.find_element('view all', '//*[@class="pull-right link-all"]/a[contains(@href, "videos")]')
                        link = link_element.get_attribute('href')
                        if link: self.driver.get(link)
                        else:
                            self.driver.get(f'https://adultprime.com/studios/search?q={self.adultprime.category}')
                            link_element = self.find_element('view all', '//*[@class="pull-right link-all"]/a[contains(@href, "videos")]')
                            link = link_element.get_attribute('href')
                            if link: self.driver.get(link)
                            else:
                                SendAnEmail(f"We don't find this {self.adultprime.category} category")
                                return False
                        return True
            next_page = self.find_element('next_page', "a.page-link.next", By.CSS_SELECTOR)
            if next_page:
                self.click_element('next_page', "a.page-link.next", By.CSS_SELECTOR)
            else:
                break
        return False

    
    def download_all_adultprime_channels_video(self):
        '''
        This function is responsible for downloading videos from various channels on the AdultPrime website.
        It iterates over a list of channel names and retrieves videos from each channel using the adultprime_get_video and adultprime_download_video functions.
        '''
        website_name = ['Clubsweethearts','Distorded','SinfulXXX','Youngbusty','Industryinvaders','Manupfilms','Sweetfemdom']
        for website in website_name:
            url = f'https://adultprime.com/studios/videos?website={website}'
            videos_dict = self.adultprime_get_video(url, True)
            self.adultprime_download_video(videos_dict)

    def adultprime_get_video(self, url:str='', channel:bool=False):
        '''
        Parameter :
        url:str = Default is empty str, channel's url or anyother url of aDultprime website
        channel: bool = Default is False, if url is channels url than make this True
        '''
        self.calculate_old_date(self.adultprime.more_than_old_days_download)
        video_detailes = {'collection_name':'','video_list':[]}
        videos_urls = []
        if channel: self.driver.get(url)
        else:
            if not self.get_adultprime_category(): 
                return None
        self.random_sleep(3,5)
        new_csv = 'website' in url
        video_detailes['collection_name'] = url.split('=')[-1].lower()+ '_videos' if new_csv else self.adultprime.website_name + '_videos'
        website_name = f"adultprime_{video_detailes['collection_name']}" if new_csv else self.adultprime.website_name
        self.make_csv(website_name, new=new_csv)
        df_url = self.column_to_list(website_name,'Url')
        max_video = self.adultprime.numbers_of_download_videos
        while len(videos_urls) < max_video:
            row_element = self.find_element('row', "//div[@class='row portal-grid']")
            li_tags = row_element.find_elements(By.CSS_SELECTOR, ".model-wrapper.portal-video-wrapper")

            for i, li_tag in enumerate(li_tags, start=1):
                # Get video date and check if it's old
                all_timestamp = li_tag.find_element(By.XPATH,'//span[@class="description-releasedate"]')
                video_date = all_timestamp.get_attribute("innerHTML").replace('<i class="fa fa-calendar"></i> ',"")
                video_url = li_tag.find_element(By.CSS_SELECTOR, "a[href^='/studios/video']")
                if video_date and self.date_older_or_not(video_date):
                    video_url = li_tag.find_element(By.CSS_SELECTOR, "a[href^='/studios/video']").get_attribute("href")
                    post_url = li_tag.find_element(By.CSS_SELECTOR, ".ratio-16-9").get_attribute("style").split('url("')[-1].split('")')[0]
                    
                    if not post_url:
                        self.random_sleep(5, 7)
                        post_url = li_tag.find_element(By.CSS_SELECTOR, ".ratio-16-9").get_attribute("style").split('url("')[-1].split('")')[0]
                    
                    # Check if video URL is new and add it to the list
                    if video_url not in df_url and video_url not in [item['video_url'] for item in videos_urls]:
                        videos_urls.append({"video_url": video_url, 'post_url': post_url})

                if len(videos_urls) >= max_video:
                    break

            # Go to the next page if available
            next_page = self.find_element('next_page', "a.page-link.next", By.CSS_SELECTOR)
            if next_page:
                self.click_element('next_page', "a.page-link.next", By.CSS_SELECTOR)
            else:
                break
        video_detailes['video_list'] = videos_urls
        return video_detailes
    
    def adultprime_download_video(self,videos_dict : dict):
        videos_urls = videos_dict['video_list']
        collection_name = videos_dict['collection_name']
        collection_path = self.create_or_check_path(self.adultprime_category_path,sub_folder_=collection_name)
        new_csv= collection_name != 'adultprime_videos'
        website_name = f"adultprime_{collection_name}" if new_csv else self.adultprime.website_name

        for idx, video_url in enumerate(videos_urls):
            self.driver.get(video_url['video_url'])
            
            self.random_sleep(5,6)
            tmp = {
                    "Likes" : "",
                    "Disclike" :"",
                    "Url" : video_url['video_url'], 
                    "Category" : videos_dict['collection_name'],
                    "video_download_url" : '',
                    "Title" : '',
                    "Discription" : "",
                    "Release-Date" : "",
                    "Poster-Image_uri" : video_url['post_url'],
                    "poster_download_uri" : '',
                    "Video-name" : '',
                    "Photo-name" : '',
                    "Pornstarts" : '',
                    "Username" : self.adultprime.website_name,
                }
            try:
                likes_count = self.find_element('Likes count','//span[@class="up-down-votes"]')
                if likes_count :
                    like_dislike_count = str(likes_count.text).split("/")
                    tmp['Likes'] = like_dislike_count[0].strip()
                    tmp['Disclike'] = like_dislike_count[1].strip()

                Title = self.find_element('Title','//h2[@class="update-info-title "]')
                if Title :
                    tmp['Title'] = Title.text

                Release = self.find_element('release date', "#theatre-row > div.col-xs-12.col-md-8 > div.update-info-container > div > div.update-info-site > div.vote-container.pull-right.mt-25 > p > b:nth-child(2)", By.CSS_SELECTOR)
                if Release :
                    tmp['Release-Date'] = Release.text

                Discription = self.find_element('Discription','//p[@class="update-info-line ap-limited-description-text regular hidden-xs"]')
                if Discription :
                    tmp['Discription'] = Discription.text
                
                porn_starts = self.driver.find_elements(By.XPATH,'//*[@id="theatre-row"]/div[1]/div[2]/div/p[3]/a')
                if porn_starts:
                    porn_start_name = ''
                    for i in porn_starts:
                        porn_start_name += f'{i.text},'
                    tmp['Pornstarts'] = porn_start_name.rstrip(',')

                video_name = f"adultprime_{collection_name.replace('_videos', '')}_{self.sanitize_title(tmp['Title'])}".replace('adultprime_adultprime','adultprime')
                tmp['Photo-name'] = f'{video_name}.jpg'
                tmp['Video-name'] = f'{video_name}.mp4'

                v_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
                p_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
                tmp['poster_download_uri'] = p_url  
                tmp['video_download_url'] = v_url

                response = requests.get(video_url['post_url'])
                with open(os.path.join(collection_path, f'{video_name}.jpg'), 'wb') as f:f.write(response.content)
 
                local_filename =  os.path.join(collection_path, f'{video_name}.mp4')
                FullHD_link = self.driver.find_elements(By.XPATH, '//a[@class="stream-quality-selection download-link"]')
                if len(FullHD_link) > 2:
                    decoded_url = FullHD_link[2].get_attribute('href')
                    self.random_sleep(2,3)
                    self.download_video_from_request(decoded_url, local_filename)
                else:continue

                self.set_data_of_csv(website_name,tmp,video_name)
            except Exception as e:
                print('Error:', e)

    def whorny_login(self):
        ''' 
        This function automates the login process for the WhornyFilms  website.

        Returns:
            bool: True if login is successful, False otherwise.
        '''
        # Configurations
        self.whorny = configuration.objects.get(website_name='whorny')
        self.whorny_category_path = self.create_or_check_path('whorny_category_videos')

        # Login process
        # self.get_driver()
        for i in range(2):
            self.driver.get('https://whornyfilms.com/MembersPage/login')
            self.load_cookies(self.whorny.website_name)
            if self.find_element('Sign Out', '//*[text()="Logout"]'):
                return True

            self.input_text(self.whorny.username, 'username_input', '//*[@placeholder="Username/Email"]')
            self.input_text(self.whorny.password, 'password_input','//*[@placeholder="Password"]')
            self.click_element('login btn', '//*[@type="submit"]')

            if self.find_element('Sign Out', '//*[text()="Logout"]'):
                self.get_cookies(self.whorny.website_name)
                return True
        return False
    
    def get_element_attribute(self, locator, attribute, max_attempts=10, wait_time=1):
        attempts = 0
        while attempts < max_attempts:
            try:
                element = self.driver.find_element(By.XPATH,locator)
                attribute_value = element.get_attribute(attribute)
                return attribute_value
            except Exception as e:
                print("Stale element reference exception occurred. Retrying...")
                attempts += 1
                time.sleep(wait_time)
        print(f"Failed to retrieve attribute '{attribute}' after {max_attempts} attempts.")
        return None
    
    def extract_specific_links(text, base_url, pattern_url):
        pattern = rf'{re.escape(base_url)}.*{re.escape(pattern_url)}'
        links = re.findall(pattern, text)
        return links
    
    def download_whorny_videos(self):
        self.calculate_old_date(self.whorny.more_than_old_days_download)
        videos_urls = 0
        self.random_sleep(3,5)
        website_name = self.whorny.website_name
        df_url = self.column_to_list(website_name,'Url')
        max_video = self.whorny.numbers_of_download_videos
        collection_name = 'whornyfilms_videos'
        collection_path = self.create_or_check_path(self.whorny_category_path, sub_folder_=collection_name)
        while videos_urls < max_video:
            self.driver.get('https://members.whornyfilms.com/search-and-filter/')
            breakpoint()
            container = self.find_element('container', '//*[@class="dce-posts-wrapper dce-wrapper-grid"]')
            all_link = [a.get_attribute('href') for a in container.find_elements(By.TAG_NAME, 'a')]

            for link in all_link:
                if videos_urls  >= max_video:break
                self.driver.get(link)
                video_url = self.driver.current_url
                self.random_sleep(5,5)
                if video_url not in df_url:
                    Title = self.find_element('title', '//h3').text
                    a_tag = self.find_element('download btn',  f"//a[contains(., 'DOWNLOAD VIDEO AND GALLERY')]").get_attribute('href')
                    if a_tag :
                        match = re.search(r'/(\d{4}/\d{2}/\d{2})/',  a_tag)
                        date = match.group(1) if match else None
                        if date and self.date_older_or_not(date):
                            try:
                                iframe = self.find_element('iframe', 'iframe', By.TAG_NAME)
                                self.driver.switch_to.frame(iframe)
                                post_url = self.find_element('video tag', 'video', By.TAG_NAME).get_attribute('data-poster')
                                self.driver.switch_to.default_content()
                                tmp = {
                                    "Likes" : "",
                                    "Disclike" :"",
                                    "Url" : video_url, 
                                    "Category" : collection_name,
                                    "video_download_url" : '',
                                    "Title" : '',
                                    "Discription" : "",
                                    "Release-Date" : "",
                                    "Poster-Image_uri" : post_url,
                                    "poster_download_uri" : '',
                                    "Video-name" : '',
                                    "Photo-name" : '',
                                    "Pornstarts" : '',
                                    "Username" : self.whorny.website_name,
                                }
                                likes_element = self.find_element('like', 'span.elementor-button-counter', By.CSS_SELECTOR)

                                tmp['Likes'] = 0 if not likes_element else int(likes_element.text)
                                tmp['Disclike'] = 0


                                if Title :
                                    tmp['Title'] = Title
                                
                                
                                tmp['Release-Date'] = date

                                tmp['Discription'] = ''
 
                                tmp['Pornstarts'] = ''

                                video_name = f"{collection_name.replace('_videos', '')}_{self.sanitize_title(Title)}"
                                tmp['Photo-name'] = f'{video_name}.jpg'
                                tmp['Video-name'] = f'{video_name}.mp4'

                                v_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
                                p_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
                                tmp['poster_download_uri'] = p_url
                                tmp['video_download_url'] = v_url

                                payload = {}
                                headers = {
                                'Referer': 'https://iframe.mediadelivery.net/'
                                }
                                

                                response = requests.request("GET", post_url, headers=headers, data=payload)
                                with open(os.path.join(collection_path, f'{video_name}.jpg'), 'wb') as file:
                                    file.write(response.content)
                                
                                self.click_element('download button', '//*[@data-id="dd55478"]')
                                url = self.find_element('download button', '//*[@data-id="1a4b7e6"]').find_element(By.TAG_NAME, 'a').get_attribute('href')
                                headers = {
                                    'Referer': 'https://downloads.whornyfilms.com/', 
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',                                'Accept-Encoding': 'gzip, deflate, br, zstd',                               
                                    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                                    }
                                self.download_video_from_request(url, os.path.join(collection_path, f'{video_name}.mp4'), headers)
                                self.set_data_of_csv(self.whorny.website_name,tmp,video_name)
                                print(f'video download count: {videos_urls+1}')
                                videos_urls+=1
                            except:
                                continue
            # Go to the next page if available
            self.driver.get('https://members.whornyfilms.com/search-and-filter/')
            next_btn = self.click_element('next', '//*[@class="dce-pagination"]')
            if not next_btn:break


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



    def revsharecash_login(self):
        self.revsharecash = configuration.objects.get(website_name='revsharecash')
        self.revsharecash_category_path = self.create_or_check_path('revsharecash_category_videos')

        self.get_driver()
        self.driver.implicitly_wait(10)
        websites = {
            'defloration':'https://4kpornxxx:th4f2baw@defloration.tv/members/',
            'flexyteens':'https://4kpornxxx:th4f2baw@flexyteens.com/members/',
            'virginmassage':'https://4kpornxxx:th4f2baw@virginmassage.com/members/',
            'underwatershow':'https://4kpornxxx:th4f2baw@underwatershow.com/members/',
        }

        for website, url in websites.items():
            if website == 'defloration':
                self.defloration_videos_download(url)
            elif website == 'flexyteens':
                self.flexyteens_videos_download(url)
            elif website == 'virginmassage':
                self.virginmassage_videos_download(url)
            elif website == 'underwatershow':
                self.underwatershow_videos_download(url)


    def defloration_videos_download(self, website_url=None):
        self.driver.get(website_url)

        website_name = 'defloration'
        csv_name = 'revsharecash_defloration'

        collection_name = 'defloration_videos'
        collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_='defloration_videos')


        self.make_csv(csv_name, new=True)
        df_url = self.column_to_list(csv_name,'Url')

        max_video = self.revsharecash.numbers_of_download_videos
        found_videos = 0

        while found_videos < max_video:

            # get all videos link
            videos_url = []
            all_block = self.driver.find_elements(By.CLASS_NAME, "images_block_content")
            for block in all_block:
                all_thumb = block.find_elements(By.CLASS_NAME, 'thumb_block')
                for thumb in all_thumb:
                    videos_url.append(thumb.find_element(By.TAG_NAME, 'a').get_attribute('href'))

            # scraping and download process
            for url in videos_url:
                if found_videos == max_video:
                    break
                if url not in df_url:
                    self.driver.get(url)
                    video_block = self.driver.find_element(By.CLASS_NAME, "one_video_block")

                    title = video_block.find_element(By.CLASS_NAME, 'video_title').text.split('(')[0].strip()
                    video_name = f"{collection_name.replace('_videos', '')}_{url.split('/')[-1]}_{self.sanitize_title(title)}"
                    
                    tmp = {}
                    tmp['Title'] = title
                    tmp['Discription'] = "Not available"
                    tmp['Release-Date'] = "Not available"
                    tmp['Likes'] = "Not available"
                    tmp['Disclike'] = "Not available"
                    tmp['Url'] = self.driver.current_url
                    tmp['Poster-Image_uri'] = self.driver.find_element(By.CLASS_NAME, "video_screenshot").get_attribute('src')
                    tmp['Category'] = website_name
                    tmp['video_download_url'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
                    tmp['poster_download_uri'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
                    tmp['Video-name'] = f'{video_name}.mp4'
                    tmp['Photo-name'] = f'{video_name}.jpg'
                    tmp['Pornstarts'] = "Not available"
                    tmp['Username'] = self.revsharecash.website_name

                    response = requests.get(tmp['Poster-Image_uri'])
                    with open(os.path.join(collection_path, f'{video_name}.jpg'), 'wb') as file:
                        file.write(response.content)

                    url = self.driver.find_elements(By.XPATH, '//a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
                    self.download_video_from_request(url, os.path.join(collection_path, tmp['Video-name']))

                    self.set_data_of_csv(csv_name,tmp,video_name)
                    found_videos+=1


            if not found_videos >= max_video:
                # pagignation
                self.driver.get(website_url)
                self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
                website_url = self.driver.current_url


    def flexyteens_videos_download(self, website_url=None):
        self.driver.get(website_url)

        website_name = 'flexyteens'
        csv_name = 'revsharecash_flexyteens'

        collection_name = 'flexyteens_videos'
        collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_='flexyteens_videos')

        self.make_csv(csv_name, new=True)
        df_url = self.column_to_list(csv_name,'Url')

        max_video = self.revsharecash.numbers_of_download_videos
        found_videos = 0

        while found_videos < max_video:

            # get all videos link
            videos_url = []
            all_block = self.driver.find_elements(By.CLASS_NAME, "images_block_content")
            for block in all_block:
                all_thumb = block.find_elements(By.CLASS_NAME, 'thumb_block')
                for thumb in all_thumb:
                    videos_url.append(thumb.find_element(By.TAG_NAME, 'a').get_attribute('href'))

            # scraping and download process
            for url in videos_url:
                if found_videos >= max_video:
                    break
                if url not in df_url:
                    self.driver.get(url)
                    video_block = self.driver.find_element(By.CLASS_NAME, "one_video_block")

                    title = video_block.find_element(By.CLASS_NAME, 'video_title').text.split('(')[0].strip()
                    video_name = f"{collection_name.replace('_videos', '')}_{url.split('/')[-1]}_{self.sanitize_title(title)}"

                    tmp = {}
                    tmp['Title'] = title
                    tmp['Discription'] = "Not available"
                    tmp['Release-Date'] = "Not available"
                    tmp['Likes'] = "Not available"
                    tmp['Disclike'] = "Not available"
                    tmp['Url'] = self.driver.current_url
                    tmp['Poster-Image_uri'] = self.driver.find_element(By.CLASS_NAME, "video_screenshot").get_attribute('src')
                    tmp['Category'] = website_name
                    tmp['video_download_url'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
                    tmp['poster_download_uri'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
                    tmp['Video-name'] = f'{video_name}.mp4'
                    tmp['Photo-name'] = f'{video_name}.jpg'
                    tmp['Pornstarts'] = "Not available"
                    tmp['Username'] = self.revsharecash.website_name

                    response = requests.get(tmp['Poster-Image_uri'])
                    with open(os.path.join(collection_path, f'{video_name}.jpg'), 'wb') as file:
                        file.write(response.content)

                    url = self.driver.find_elements(By.XPATH, '//a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
                    self.download_video_from_request(url, os.path.join(collection_path, tmp['Video-name']))

                    self.set_data_of_csv(csv_name, tmp, video_name)
                    found_videos += 1


            if not found_videos >= max_video:
                # pagignation
                self.driver.get(website_url)
                self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
                website_url = self.driver.current_url

    def virginmassage_videos_download(self, website_url=None):
        self.driver.get(website_url)

        website_name = 'virginmassage'
        csv_name = 'revsharecash_virginmassage'

        collection_name = 'virginmassage_videos'
        collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_='virginmassage_videos')

        self.make_csv(csv_name, new=True)
        df_url = self.column_to_list(csv_name,'Url')

        max_video = self.revsharecash.numbers_of_download_videos
        found_videos = 0

        while found_videos < max_video:

            # get all videos link, scraping and download process
            all_block = self.driver.find_elements(By.CLASS_NAME, "one_video_block")
            for block in all_block:
                if found_videos >= max_video:
                    break
                
                video_url = block.find_element(By.CLASS_NAME, "one_video_block_content").find_element(By.TAG_NAME,'a').get_attribute('href')
                if video_url not in df_url:
                    title = block.find_element(By.CLASS_NAME, 'video_title1').text.split('(')[0].strip()
                    video_name = f"{collection_name.replace('_videos', '')}_{video_url.split('/')[-1]}_{self.sanitize_title(title)}"

                    tmp = {}
                    tmp['Title'] = title
                    tmp['Discription'] = "Not available"
                    tmp['Release-Date'] = "Not available"
                    tmp['Likes'] = "Not available"
                    tmp['Disclike'] = "Not available"
                    tmp['Url'] = video_url
                    tmp['Poster-Image_uri'] = block.find_element(By.CLASS_NAME, "video_screenshot").get_attribute('src')
                    tmp['Category'] = website_name
                    tmp['video_download_url'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
                    tmp['poster_download_uri'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
                    tmp['Video-name'] = f'{video_name}.mp4'
                    tmp['Photo-name'] = f'{video_name}.jpg'
                    tmp['Pornstarts'] = "Not available"
                    tmp['Username'] = self.revsharecash.website_name

                    response = requests.get(tmp['Poster-Image_uri'])
                    with open(os.path.join(collection_path, f'{video_name}.jpg'), 'wb') as file:
                        file.write(response.content)

                    url = block.find_elements(By.XPATH, './/a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
                    self.download_video_from_request(url, os.path.join(collection_path, tmp['Video-name']))

                    self.set_data_of_csv(csv_name, tmp, video_name)
                    found_videos += 1

            if not found_videos >= max_video:
                # pagignation
                self.driver.get(website_url)
                self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
                website_url = self.driver.current_url
    
    def underwatershow_videos_download(self, website_url=None):
        # try:
            self.driver.get(website_url)

            website_name = 'underwatershow'
            csv_name = 'revsharecash_underwatershow'

            collection_name = 'underwatershow_videos'
            collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_='underwatershow_videos')

            self.make_csv(csv_name, new=True)
            df_url = self.column_to_list(csv_name,'Url')

            max_video = self.revsharecash.numbers_of_download_videos
            found_videos = 0

            while found_videos < max_video:

                # get all videos link, scraping and download process
                all_block = self.driver.find_elements(By.CLASS_NAME, "one_video_block")
                for block in all_block:
                    if found_videos >= max_video:
                        break
                    print(block.text)
                    video_url_dd = block.find_element(By.CLASS_NAME, "video_footer")
                    if str(video_url_dd.text).strip() == "":
                        continue
                    video_url = video_url_dd.find_element(By.TAG_NAME,'a').get_attribute('href')
                    if video_url not in df_url:

                        title = block.find_element(By.CLASS_NAME, 'video_title1').text.split('(')[0].strip()
                        video_name = f"{collection_name.replace('_videos', '')}_{video_url.split('/')[-1]}_{self.sanitize_title(title)}"

                        tmp = {}
                        tmp['Title'] = title
                        tmp['Discription'] = "Not available"
                        tmp['Release-Date'] = "Not available"
                        tmp['Likes'] = "Not available"
                        tmp['Disclike'] = "Not available"
                        tmp['Url'] = video_url
                        tmp['Poster-Image_uri'] = block.find_element(By.CLASS_NAME, "video_screenshot").get_attribute('src')
                        tmp['Category'] = website_name
                        tmp['video_download_url'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
                        tmp['poster_download_uri'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
                        tmp['Video-name'] = f'{video_name}.mp4'
                        tmp['Photo-name'] = f'{video_name}.jpg'
                        tmp['Pornstarts'] = "Not available"
                        tmp['Username'] = self.revsharecash.website_name

                        response = requests.get(tmp['Poster-Image_uri'])
                        with open(os.path.join(collection_path, f'{video_name}.jpg'), 'wb') as file:
                            file.write(response.content)

                        url = block.find_elements(By.XPATH, './/a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
                        self.download_video_from_request(url, os.path.join(collection_path, tmp['Video-name']))

                        self.set_data_of_csv(csv_name, tmp, video_name)
                        found_videos += 1

                if not found_videos >= max_video:
                    # pagignation
                    self.driver.get(website_url)
                    self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
                    website_url = self.driver.current_url
        # except Exception as e:
        #     print(e)

    def sexmex_login(self):
        self.sexmex = configuration.objects.get(website_name='sexmex')
        self.sexmex_category_path = self.create_or_check_path('sexmex_category_videos')

        # self.get_driver()
        self.driver.get('https://members.sexmex.xxx/members/')

        self.load_cookies(self.sexmex.website_name)
        if self.find_element('LOGOUT', '//*[text()="LOGOUT"]'):return True

        for i in range(3):
            self.input_text(self.sexmex.username,'Username','uid', By.NAME)
            self.input_text(self.sexmex.password,'Password','pwd', By.NAME)
            self.click_element('submit btn', '//*[@type="submit"]')
            self.random_sleep(5)
            if self.find_element('LOGOUT', '//*[text()="LOGOUT"]'):
                self.get_cookies(self.sexmex.website_name)
                return True
        return False
    

    def sexmax_video_download(self):
        csv_name = 'sexmex'
        df_url = self.column_to_list(csv_name,'Url')

        max_video = self.sexmex.numbers_of_download_videos
        found_videos = 0

        video_list = []
        self.click_element('see more', 'float-end', By.CLASS_NAME)

        while found_videos < max_video:
            section = self.find_element('section', '/html/body/div[3]/div[1]')
            all_div = section.find_elements(By.XPATH, './div')
            for div in all_div:
                scene_date = div.find_element(By.CLASS_NAME, 'scene-date').text
                self.calculate_old_date(self.sexmex.more_than_old_days_download)
                if self.date_older_or_not(scene_date):
                    link = div.find_element(By.XPATH, '//h5/a').get_attribute('href')
                    if link not in df_url:
                        video_list.append(link)
                        found_videos+=1
                    if found_videos == max_video:
                        break

            if found_videos == max_video:break
            self.click_element('next', '//*[text()="Next >"]')
            self.random_sleep(4,7)


        for link in video_list:
            self.driver.get(link)
            try:
                video_title = self.find_element('title', '//h4').text
                video_name = f"sexmex_{self.sanitize_title(video_title)}"
                discription = self.find_element('description', '//*[@class="panel-body"]/p').text
                model_name = self.find_element('pornstar', 'update_models', By.CLASS_NAME).text.replace(':', '').strip()
                v_url = f'http://208.122.217.49:8000{self.sexmex_category_path.replace(self.base_path,"")}/{video_name}.mp4'
                p_url = f'http://208.122.217.49:8000{self.sexmex_category_path.replace(self.base_path,"")}/{video_name}.jpg'
                photo_url = self.find_element('photo url','video', By.TAG_NAME).get_attribute('poster')
                if photo_url:
                    response = requests.get(photo_url)
                    with open(os.path.join(self.sexmex_category_path, f'{video_name}.jpg'), 'wb') as f:f.write(response.content)

                tmp = {}
                tmp['Likes'] = "Not available"
                tmp['Disclike'] = "Not available"
                tmp['Url'] = link
                tmp['Title'] = video_title
                tmp['Discription'] = discription
                tmp['Release-Date'] = self.find_element('date', '//*[@class="float-end"]/p').text
                tmp['Poster-Image_uri'] = photo_url
                tmp['poster_download_uri'] = p_url
                tmp['Video-name'] = f'{video_name}.mp4'
                tmp['video_download_url'] = v_url
                tmp['Photo-name'] = f'{video_name}.jpg'
                tmp['Pornstarts'] = model_name     
                tmp['Category'] = "Not available"
                tmp['Username'] =  self.sexmex.website_name                      
                
                video_url = self.find_element('video url', '//*[text()="1080p"]').get_attribute('value')
                self.download_video_from_request(video_url, os.path.join(self.sexmex_category_path, f'{video_name}.mp4'))

                self.set_data_of_csv(self.sexmex.website_name,tmp,video_name)
            except :
                pass


    def fivekteen_login2(self):

        def get_captcha_token(site_key):
            from twocaptcha_extension_python import TwoCaptcha
            self.extra_args.append(TwoCaptcha(api_key="6e00098870d05c550b921b362c2abde8").load())
            solver = TwoCaptcha('6e00098870d05c550b921b362c2abde8')
            g_response = solver.recaptcha(site_key, 'https://members.5kporn.com/login')

        self.fivekteen = configuration.objects.get(website_name='5kteen')
        self.fivekteen_category_path = self.create_or_check_path('fivekteen_category_videos')

        # Login process
        self.driver_type = 'normal'

        self.get_driver()
        for i in range(2):

            self.driver.get('https://members.5kporn.com/')
            # self.load_cookies(self.fivekteen.website_name, 'https://members.5kporn.com/')

            self.random_sleep()

            if self.find_element('Sign Out', "//button[contains(normalize-space(.), 'Logout')]"):
                self.get_cookies(self.fivekteen.website_name)
                return True
            else :
                self.driver.get('https://members.5kporn.com/login') if not self.driver.current_url == 'https://members.5kporn.com/login' else None

            self.input_text(self.fivekteen.username, 'username_input', '//*[@id="username"]')
            self.input_text(self.fivekteen.password, 'password_input','//*[@id="password"]')
            # self.click_element('solve captcha', '//button[@id="recaptchaBindedElement0"]')
            # site_key_ele = self.find_element('SITE-KEY','g-recaptcha',By.CLASS_NAME)
            # if site_key_ele:
            #     site_key = site_key_ele.get_attribute('data-sitekey')
            #     solver = TwoCaptcha('6e00098870d05c550b921b362c2abde8')
            #     g_response = solver.recaptcha(site_key,'https://members.5kporn.com/login')

            #     if g_response != 0:
            #         self.driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "{}";'.format(g_response['code']))
            #     self.driver.execute_script(f'''var els=document.getElementsByName("g-recaptcha-response");for (var i=0;i<els.length;i++) {{els[i].value = "{g_response}";}}''')
            #     self.driver.execute_script(f'''var els=document.getElementsByName("g-recaptcha-response");for (var i=0;i<els.length;i++) {{els[i].value = "{g_response['code']}";}}''')
            #     # # to solvee the captcha
            #     g_response = self.solve_2captcha(site_key=site_key, site_url=self.driver.current_url)
            #     self.driver.execute_script(f'''var els=document.getElementsByName("g-recaptcha-response");for (var i=0;i<els.length;i++) {{els[i].value = "{g_response}";}}''')
            self.click_element('login btn', '//*[@type="submit"]')
            # self.find_element('login btn', '//*[@type="submit"]')
            # self.find_element('captcha', '//*[@title="recaptcha challenge expires in two minutes"]')
            if self.find_element('Sign Out', "//button[contains(normalize-space(.), 'Logout')]"):
                self.get_cookies(self.fivekteen.website_name)
                return True
        return False

    def fivekteen_login(self):
        def download_image(image_url, save_path):
            """Download an image from a URL and save it to a local file."""
            try:
                # Send a GET request to the image URL
                response = requests.get(image_url)
                
                # Check if the request was successful
                if response.status_code == 200:
                    # Open the file in binary write mode and write the content
                    with open(save_path, 'wb') as file:
                        file.write(response.content)
                    print(f"Image successfully downloaded and saved to {save_path}")
                else:
                    print(f"Failed to retrieve the image. Status code: {response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")
                
        clientKey = "6e00098870d05c550b921b362c2abde8"
        url = "https://members.5kporn.com/login"
        API_KEY = '6e00098870d05c550b921b362c2abde8'
        solver = TwoCaptcha(API_KEY)
        
        def most_frequent_number(numbers):
            from collections import Counter

            """Find the most frequent number in a list."""
            if not numbers:
                raise ValueError("The list is empty.")
            
            # Count occurrences of each number
            counts = Counter(numbers)
            
            # Find the number with the highest count
            most_common = counts.most_common(1)[0]  # Get the most common number and its count
            return most_common[0]
        
        def solve_captcha():
            
            def get_most_frequent_link(image_urls):
                from collections import Counter
                
                """Get the most frequent image link from the web elements."""
                # Extract image URLs from the web elements
                
                if not image_urls:
                    raise ValueError("No image URLs found.")
                
                # Count occurrences of each URL
                url_counts = Counter(image_urls)
                
                # Find the most common URL
                most_common_url = url_counts.most_common(1)[0][0]
                return most_common_url
            
            loop_run = True
            while loop_run :
                
                self.driver.switch_to.default_content()
                iframe = self.find_element('captcha iframe','//*[@title="recaptcha challenge expires in two minutes"]')
                self.driver.switch_to.frame(iframe)
                descriptions = self.find_element('Captcha description','//*[@id="rc-imageselect"]/div[2]/div[1]/div[1]')
                captcha_img_src = get_most_frequent_link([ i.find_element(By.TAG_NAME,'img').get_attribute('src') for i in self.driver.find_elements(By.TAG_NAME,'td')])
                download_image(captcha_img_src,"/media/rk/600/workspace/sajal/adult-webscraping/downloads/payload.jpeg")
                
                all_td = self.driver.find_elements(By.TAG_NAME,'td')
                if len(all_td) == 9:
                    row= 3
                    col = 3
                else :
                    row = 4
                    col = 4
                result = solver.grid(file="/media/rk/600/workspace/sajal/adult-webscraping/downloads/payload.jpeg",hintText = descriptions.text, rows=row, cols=col)
                    
                if 'code' in result.keys():
                    code_number_list = [int(i) for i in result['code'].replace('click:','').split('/') if i.isdigit()]
                    
                    for td in all_td :
                        if all_td.index(td)+1 in code_number_list :
                            td.click()
                                
                
                self.click_element('captcha verify btn','recaptcha-verify-button',By.ID)
                self.random_sleep()
                if self.find_element('captcha verify btn','recaptcha-verify-button',By.ID) : continue
                
                

                self.driver.switch_to.default_content()
                sub_btn = self.find_element('login btn', '//*[@type="submit"]', timeout=2)
                if sub_btn :
                    sub_btn.submit()
                
                self.random_sleep(5,10)
                if self.find_element('Sign Out', "//button[contains(normalize-space(.), 'Logout')]"):
                    self.get_cookies(self.fivekteen.website_name)
                break


        self.fivekteen = configuration.objects.get(website_name='5kteen')
        self.fivekteen_category_path = self.create_or_check_path('fivekteen_category_videos')
        # Login process
        # self.driver_type = 'normal'

        self.get_driver()
        for i in range(2):

            self.driver.get('https://members.5kporn.com/')
            self.load_cookies(self.fivekteen.website_name, 'https://members.5kporn.com/')
            self.random_sleep()

            if self.find_element('Sign Out', "//button[contains(normalize-space(.), 'Logout')]"):
                self.get_cookies(self.fivekteen.website_name)
                return True
            else :
                self.driver.get('https://members.5kporn.com/login') if not self.driver.current_url == 'https://members.5kporn.com/login' else None
                # return False




            self.input_text(self.fivekteen.username, 'username_input', '//*[@id="username"]')
            self.input_text(self.fivekteen.password, 'password_input', '//*[@id="password"]')
            sub_btn = self.find_element('login btn', '//*[@type="submit"]')
            sub_btn.submit()
            solve_captcha()
            
            self.random_sleep()
            if self.find_element('Sign Out', "//button[contains(normalize-space(.), 'Logout')]"):
                self.get_cookies(self.fivekteen.website_name)
                return True
        return False
    
    def download_fivek_teen_video(self):
        self.calculate_old_date(self.fivekteen.more_than_old_days_download)
        video_count = self.fivekteen.numbers_of_download_videos

        videos_urls = []
        df_url = self.column_to_list(self.fivekteen.website_name,'Url')

        page_count = 2
        while True:
            self.driver.get('https://members.5kporn.com/?site=2')
            all_video = self.driver.find_elements(By.XPATH,'//*[@class="ep"]')
            
            for video in all_video:
                date = video.find_element(By.XPATH, './div[1]/div[1]')
                if self.date_older_or_not(date.text):
                    video_url = video.find_element(By.XPATH ,'./div[2]/div/a').get_attribute('href')
                    post_url = video.find_element(By.XPATH ,'./div[2]/div/a/div/img[1]').get_attribute('src')
                    if post_url and video_url not in df_url and video_count > len(videos_urls):
                        videos_urls.append({"video_url": video_url, 'post_url': post_url})
                    if video_count == len(videos_urls):
                        break
            if video_count == len(videos_urls):
                break

            self.driver.get(f'https://members.5kporn.com/?site=2&page={page_count}')
            page_count+=1

        for item in videos_urls:
            self.driver.get(item['video_url'])
            tmp = {}

            video_name = f'''fivek_teen_{self.sanitize_title(self.find_element('title', '//*[contains(text(), "Title:")]').text.split('Title: ')[-1])}'''
            tmp['Likes'] = 'Not available'
            tmp['Disclike'] = 'Not available'
            tmp['Url'] = item['video_url']
            tmp['Category'] = 'Not available'
            tmp['Title'] = video_name
            tmp['Discription'] = self.find_element('Discription', '/html/body/div[2]/div[4]/div[2]/div/div/div[2]').text.split('Episode Summary\n')[-1]
            tmp['Release-Date'] = self.find_element('release date', '//*[contains(text(), "Published:")]').text.split('Published: ')[-1]
            tmp['Poster-Image_uri'] = item['post_url']
            tmp['video_download_url'] = f'http://208.122.217.49:8000{self.fivekteen_category_path.replace(self.base_path,"")}/{video_name}.mp4'
            tmp['poster_download_uri'] = f'http://208.122.217.49:8000{self.fivekteen_category_path.replace(self.base_path,"")}/{video_name}.jpg'
            tmp['Video-name'] = f'{video_name}.mp4'
            tmp['Photo-name'] = f'{video_name}.jpg'
            tmp['Pornstarts'] = self.find_element('pornstar', '//h5[contains(text(), "Starring:")]').text.split('Starring: ')[-1]
            tmp['Username'] = self.fivekteen.website_name
            self.click_element('download', '//*[@data-target="#download-modal"]')
            download_table = self.find_element('Download table','download-modal',By.ID)
            if download_table:
                self.click_element('Best quality download video','//*[@id="collapseEPS"]/div/ul/li')
            name_of_file = tmp['Video-name']
            
            file_name = self.wait_for_file_download()

            if not os.path.exists(os.path.join(self.download_path,'fivekteen_category_videos','teen')):
                os.makedirs(os.path.join(self.download_path,'fivekteen_category_videos','teen'))
            os.rename(os.path.join(self.download_path, file_name), os.path.join(self.download_path,'fivekteen_category_videos','teen', name_of_file))
            self.set_data_of_csv(self.fivekteen.website_name,tmp,video_name)


    def download_fivek_porn_video(self):
        self.calculate_old_date(self.fivekteen.more_than_old_days_download)
        video_count = self.fivekteen.numbers_of_download_videos

        csv_name = '5kporn'
        videos_urls = []

        df_url = self.column_to_list(csv_name,'Url')
        page_count = 2

        while True:
            self.driver.get('https://members.5kporn.com/?site=1')
            all_video = self.driver.find_elements(By.XPATH,'//*[@class="ep"]')
            
            for video in all_video:
                date = video.find_element(By.XPATH, './div[1]/div[1]')
                if self.date_older_or_not(date.text):
                    video_url = video.find_element(By.XPATH ,'./div[2]/div/a').get_attribute('href')
                    post_url = video.find_element(By.XPATH ,'./div[2]/div/a/div/img[1]').get_attribute('src')
                    if post_url and video_url not in df_url and video_count > len(videos_urls):
                        videos_urls.append({"video_url": video_url, 'post_url': post_url})
                    if video_count == len(videos_urls):
                        break
            if video_count == len(videos_urls):
                break

            self.driver.get(f'https://members.5kporn.com/?site=1&page={page_count}')
            page_count+=1

        for item in videos_urls:
            self.driver.get(item['video_url'])
            tmp = {}

            video_name = f'''fivek_teen_{self.sanitize_title(self.find_element('title', '//*[contains(text(), "Title:")]').text.split('Title: ')[-1])}'''
            tmp['Likes'] = 'Not available'
            tmp['Disclike'] = 'Not available'
            tmp['Url'] = item['video_url']
            tmp['Category'] = 'Not available'
            tmp['Title'] = video_name
            tmp['Discription'] = self.find_element('Discription', '/html/body/div[2]/div[4]/div[2]/div/div/div[2]').text.split('Episode Summary\n')[-1]
            tmp['Release-Date'] = self.find_element('release date', '//*[contains(text(), "Published:")]').text.split('Published: ')[-1]
            tmp['Poster-Image_uri'] = item['post_url']
            tmp['video_download_url'] = f'http://208.122.217.49:8000{self.fivekteen_category_path.replace(self.base_path,"")}/{video_name}.mp4'
            tmp['poster_download_uri'] = f'http://208.122.217.49:8000{self.fivekteen_category_path.replace(self.base_path,"")}/{video_name}.jpg'
            tmp['Video-name'] = f'{video_name}.mp4'
            tmp['Photo-name'] = f'{video_name}.jpg'
            tmp['Pornstarts'] = self.find_element('pornstar', '//h5[contains(text(), "Starring:")]').text.split('Starring: ')[-1]
            tmp['Username'] = self.fivekteen.website_name

            self.click_element('download', '//*[@data-target="#download-modal"]')
            download_table = self.find_element('Download table', 'download-modal', By.ID)
            if download_table:
                self.click_element('Best quality download video', '//*[@id="collapseEPS"]/div/ul/li')

            name_of_file = tmp['Video-name']
            file_name = self.wait_for_file_download()

            if not os.path.exists(os.path.join(self.download_path, 'fivekteen_category_videos', 'videos')):
                os.makedirs(os.path.join(self.download_path, 'fivekteen_category_videos', 'videos'))
            os.rename(os.path.join(self.download_path, file_name),
                      os.path.join(self.download_path, 'fivekteen_category_videos', 'videos', name_of_file))
            self.set_data_of_csv(self.fivekteen.website_name, tmp, video_name)

            self.set_data_of_csv(csv_name,tmp,video_name)


    def test_captcha(self):
        self.get_driver()
        self.driver.get('https://www.google.com/recaptcha/api2/demo')
        self.driver.refresh()


        pass