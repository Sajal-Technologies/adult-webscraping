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
    
    def BangBros_login(self):
        self.BangBros = configuration.objects.get(website_name='BangBros')
        self.BangBros_category_path = self.create_or_check_path('BangBros_category_videos')

        self.get_driver()
        un_authorized = False
        for _ in range(3):
            bangbrobs_url = "https://site-ma.bangbros.com/store"
            self.driver.get(bangbrobs_url)
            if un_authorized == False :
                self.load_cookies('BangBros', redirect_url=bangbrobs_url)
                self.random_sleep()
                self.driver.refresh()

            if self.find_element('username','//input[@type="text"]') :
                self.input_text(self.BangBros.username, 'username','//input[@type="text"]')
                self.input_text(self.BangBros.password, 'password','//input[@type="password"]')
                self.click_element('login btn','//button[@type="submit"]')
                self.random_sleep(10,15)
                
                if self.find_element('Un Authorized Attempt',"//span[contains(text(), 'Oops, seems like the username and/or password')]", timeout=5):
                    print('Closing chrome bcz found the unauthorized page')
                    un_authorized = True
                    self.CloseDriver()
                    self.get_driver()
                    continue

            if self.find_element('Navbar' ,'nav', By.TAG_NAME) :
                self.random_sleep(reson="to let the navbar load fully")
                if [i for i in self.driver.find_element(By.TAG_NAME,'nav').find_elements(By.TAG_NAME,'a') if i.text == "ACCOUNT" ] :
                    self.driver.refresh()
                    self.get_cookies('BangBros')
                    return True
            else :
                continue
        else :
            return False
                
    def BangBros_download_videos(self, remained_download_video_number = 0):
        
        df_url = [i.Url for i in VideosData.objects.filter(configuration = self.BangBros )]
        max_video_download_number = self.BangBros.numbers_of_download_videos + 5
        download_video_link = []
        
        for category in self.BangBros.category.all() : 
            self.driver.get(category.link)
            
            page_number = 1
            while True :
                page_number += 1
                if len(download_video_link) >= max_video_download_number :
                    break
                
                if self.find_element('All videos main DIV','/html/body/div/div[1]/div[2]/div/div[2]/section/div/div[2]/div') :
                    
                    self.find_element('First Video','/html/body/div/div[1]/div[2]/div/div[2]/section/div/div[2]/div/div[1]/div/div[1]/a', timeout=25)
                    self.random_sleep(10,15,reson="let the all videos load")
                    for main_video_div in self.find_element('All videos main DIV','/html/body/div/div[1]/div[2]/div/div[2]/section/div/div[2]/div').find_elements(By.XPATH,'./*'): 
                        tmp = {}
                        video_date_time = main_video_div.find_elements(By.CLASS_NAME,'one-list-amogcs')
                        if video_date_time :
                            video_date_time = video_date_time[-1]
                            video_date_time = video_date_time.text
                            
                            tmp['datetime'] = video_date_time
                            current_date = datetime.now()
                            given_date = datetime.strptime(video_date_time, '%b %d, %Y')
                            date_difference = current_date - given_date
                            if  date_difference > timedelta(days=self.BangBros.more_than_old_days_download):
                                
                                link = [i.get_attribute('href') for i in main_video_div.find_element(By.XPATH,'./div/div').find_elements(By.TAG_NAME,'a') if i.get_attribute('title') != ""][-1]
                                if link in df_url : 
                                    continue 
                                
                                tmp['link']  = link
                                
                                image_src = main_video_div.find_elements(By.TAG_NAME,'img')
                                if image_src :
                                    tmp['image'] = image_src[-1].get_attribute('src')
                                
                                if tmp['link'] :
                                    download_video_link.append(tmp)
                        
                        if len(download_video_link) >= max_video_download_number :
                            break
                if len(download_video_link) >= max_video_download_number :
                    break
                
                self.driver.get(f"{category.link}&page={page_number}")
                        
                        
            if download_video_link :
                for video_dict in download_video_link :
                    self.driver.get(video_dict['link'])
                    self.random_sleep(10,15,reson="let the videos to load")
                    
                    if not self.find_element("Video element", 'video', By.TAG_NAME, timeout=40) :
                        continue
                    
                    self.driver.find_elements(By.TAG_NAME,'video')
                    title = ""
                    pornstars = ""
                    likes = ""
                    descriptions = ""
                    
                    title_ele = self.find_element('Title', '/html/body/div/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[4]/div/section/div/div/h2[2]')
                    if title_ele :
                        title = title_ele.text
                        
                    pornstars_ele = self.find_element('PornStars', '/html/body/div/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[4]/div/section/div/div/div[2]/h2')
                    if pornstars_ele :
                        pornstars = pornstars_ele.text

                    likes_ele = self.find_element('Likes', '/html/body/div/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[4]/div/section/div/div/div[1]/span[1]/div')
                    if likes_ele :
                        likes = likes_ele.text
                    
                    descriptions_ele = self.find_element('descriptions', '/html/body/div/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[5]/div/section/div/p')
                    if descriptions_ele :
                        descriptions = descriptions_ele.text
                    
                    # download
                    self.click_element('download btn','/html/body/div/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/section/div[3]/div/div[5]/button')
                    self.click_element('download 1080p btn',"//button[contains(text(), '1080p')]")
                    
                    download_dir = "downloads"
                    files = []
                    for f in os.listdir(download_dir) : 
                        if os.path.isfile(os.path.join(download_dir, f)) :
                            files.append(f)
                            
                    download_file = self.wait_for_file_download(files)
                    if not download_file :
                        continue
                    
                    media_path = os.path.join(os.getcwd(),'media')
                    video_media_path = os.path.join(media_path,'videos','BangBros_category_videos',self.sanitize_title(self.BangBros.main_category))
                    image_media_path = os.path.join(media_path,'image','BangBros_category_videos',self.sanitize_title(self.BangBros.main_category))
                    os.makedirs(video_media_path, exist_ok=True)
                    os.makedirs(image_media_path, exist_ok=True)
                    
                    final_video_media_path = os.path.join(video_media_path,f'{self.sanitize_title(title)}.mp4')
                    final_image_media_path = os.path.join(image_media_path,f'{self.sanitize_title(title)}.jpg')
                    
                    download_video_file = os.path.join(os.getcwd(),'downloads',download_file)
                    if os.path.exists(download_video_file) :
                        shutil.move(download_video_file,final_video_media_path)
                    
                    if video_dict['image']:
                        response = requests.get(video_dict['image'])
                        with open(final_image_media_path, 'wb') as f: 
                            f.write(response.content)
                    
                    image_object_path = os.path.join('image','BangBros_category_videos',self.sanitize_title(self.BangBros.main_category),f'{self.sanitize_title(title)}.jpg')
                    videos_object_path = os.path.join('videos','BangBros_category_videos',self.sanitize_title(self.BangBros.main_category),f'{self.sanitize_title(title)}.mp4')
                    print("Image file : ",image_object_path)
                    print("Video file : ",videos_object_path)
                    
                    if os.path.exists(final_image_media_path) and os.path.exists(final_video_media_path) :
                        
                        videos_data_obj = VideosData.objects.create( 
                            video = videos_object_path,
                            image = image_object_path,
                            Username = self.BangBros.username,
                            Likes = int(likes.replace('Likes','')),
                            Disclike = 0,
                            Url = video_dict['link'],
                            Title = title,
                            Discription = descriptions,
                            Release_Date = video_dict['datetime'],
                            Poster_Image_url = video_dict['image'],
                            Video_name = f'{title}.mp4',
                            Photo_name = f'{title}.jpg',
                            Pornstarts = pornstars,
                            configuration = self.BangBros,
                            cetegory = category
                            )
                        max_video_download_number -= 1
                
                    if 0 <= max_video_download_number :
                        break
                        
                    
                            
                        
        # --------------------------------------------------------------------------------------
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