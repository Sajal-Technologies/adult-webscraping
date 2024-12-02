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

        for _ in range(3):
            self.load_cookies('pegas', refreash=False)
            self.driver.get("https://www.pegasproductions.com/tube?type=scenes&order=dateup")
            # href="https://pegasproductions.com/login/"
            self.random_sleep()
            self.driver.refresh()
            self.driver.delete_all_cookies()
            if self.click_element('logout btn',"//a[@href='https://pegasproductions.com/login/']") :
                self.input_text(self.pegas.username, 'username','//input[@type="text"]')
                self.input_text(self.pegas.password, 'password','//input[@type="password"]')
                self.click_element('login btn','//input[@type="submit"]')
            
            if self.find_element('logout btn',"//a[contains(text(), 'Logout')]", timeout=5) :
                self.get_cookies('pages')
                return True
                
            if not self.find_element('logout btn',"//a[contains(text(), 'Logout')]") :
                continue
            
    def pegas_download_videos(self, remained_download_video_number = 0):
        
        df_url = VideosData.objects.filter(configuration=self.revsharecash).values_list('Url', flat=True)
        max_video_download_number = self.pegas.numbers_of_download_videos + 5
        
        download_video_link = []
        all_videos_ = self.driver.find_elements(By.XPATH,'//a[@class="page"]')
        while True :
            all_videos_ = self.driver.find_elements(By.XPATH,'//div[@class="span2" and @itemprop="video"]')
            for video_div in all_videos_ :
                video_link = video_div.find_elements(By.TAG_NAME,'a')
                if video_link :
                    video_link = video_link[-1].get_attribute('href')
                    if video_link :
                        
                        if not video_link in df_url :
                            download_video_link.append(video_link)
            
                if len(download_video_link) >= max_video_download_number :
                    break
            
            if len(download_video_link) >= max_video_download_number :
                break
            
            if not self.click_element('Next page ele1','//a[@class="nextpostslink"]', timeout=5) :
                self.click_element('next page','//a[@class="page"]', timeout=5)
        
        if remained_download_video_number :
            max_video_download_number = remained_download_video_number
        else :
            max_video_download_number = self.pegas.numbers_of_download_videos
        
        for video_url in download_video_link :
            self.driver.get(video_url)
            video_title = video_url.split('/')[-1]
            video_title = 'pegas_'+self.sanitize_title(video_title)
            
            media_path = os.path.join(os.getcwd(),'media')
            video_media_path = os.path.join(media_path,'videos','pegas_category_videos',self.pegas.main_category)
            image_media_path = os.path.join(media_path,'image','pegas_category_videos',self.pegas.main_category)

            os.makedirs(video_media_path, exist_ok=True)
            os.makedirs(image_media_path, exist_ok=True)
            
            final_video_media_path = os.path.join(video_media_path,f'{video_title}.mp4')
            final_image_media_path = os.path.join(image_media_path,f'{video_title}.jpg')
            
            photo_url = ""
            if not photo_url :
                photo_url = self.find_element('photo url','//*[@itemprop="thumbnailUrl"]', By.XPATH)
                if photo_url :
                    photo_url = photo_url.get_attribute('content')

            if photo_url:
                response = requests.get(photo_url)
                with open(final_image_media_path, 'wb') as f: 
                    f.write(response.content)
            
            video__download_url = self.find_element('video url','//*[@autoplay="" and @playsinline="true" ]', By.XPATH)
            if not video__download_url :
                self.click_element('play btn','//a[@class="fp-icon fp-playbtn"]', By.XPATH)
                self.random_sleep(15,20)
                
            video__download_url = self.find_element('video url','//*[@autoplay="" and @playsinline="true" ]', By.XPATH)
            if video__download_url :
                self.download_video_from_request(video__download_url, final_video_media_path)

            if os.path.exists(final_image_media_path) and os.path.exists(final_video_media_path) :
                cetegory_obj, _ = cetegory.objects.get_or_create(category = self.sexmex.main_category)
                
                videos_data_obj = VideosData.objects.create(
                    Username = self.pegas.username,
                    Likes = 0,
                    Disclike = 0,
                    Url = self.driver.current_url,
                    Title = video_title,
                    Poster_Image_url = photo_url,
                    Video_name = f'{video_title}.mp4',
                    Photo_name = f'{video_title}.jpg',
                    configuration = self.pegas,
                    cetegory = cetegory_obj,
                    video = final_video_media_path,
                    image = final_image_media_path
                )
                max_video_download_number -= 1
                
            if 0 <= max_video_download_number :
                break
            
        else :
            self.pegas_download_videos(max_video_download_number)