from driver.get_driver import StartDriver
import json, random, os, time, requests, urllib, shutil
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


class Bot(StartDriver):
    
    def sexmex_login(self):
        self.sexmex = configuration.objects.get(website_name='Sexmex')
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
        csv_name = 'Sexmex'
        self.check_csv_exist(csv_name)
        if self.sexmax.main_category :
            self.sexmex_category_path = self.create_or_check_path(self.sexmex_category_path,sub_folder_=self.sexmax.main_category)
        
        df_url = [i.Url for i in VideosData.objects.filter(configuration=self.sexmax)]
        
        max_video = self.sexmex.numbers_of_download_videos
        found_videos = 0

        video_list = []
        self.random_sleep(4,7,reson="to let load the html of home page")
        self.click_element('see more', 'float-end', By.CLASS_NAME)
        self.driver.get('https://members.sexmex.xxx/members/category.php?id=5')

        while found_videos < max_video:
            section = self.find_element('section', '/html/body/div[3]/div[1]')
            all_div = section.find_elements(By.XPATH, './div')
            for div in all_div:
                scene_date = div.find_element(By.CLASS_NAME, 'scene-date').text
                
                if self.date_older_or_not(scene_date,self.sexmax.more_than_old_days_download):
                    link = div.find_element(By.XPATH, '//h5/a').get_attribute('href')
                    if link not in df_url:
                        video_list.append(link)
                        found_videos+=1
                    if found_videos >= max_video:
                        break

            if found_videos >= max_video:break
            self.click_element('next', '//*[text()="Next >"]')
            self.random_sleep(4,7)


        for link in video_list:
            self.driver.get(link)
            try:
                video_title = self.find_element('title', '//h4').text
                video_name = f"sexmex_{self.sanitize_title(video_title)}"
                discription = self.find_element('description', '//*[@class="panel-body"]/p').text
                model_name = self.find_element('pornstar', 'update_models', By.CLASS_NAME).text.replace(':', '').strip()
                
                v_url = f'http://208.122.217.49:8000/API/{self.sexmex_category_path.replace(self.base_path,"")}/{video_name}.mp4'
                p_url = f'http://208.122.217.49:8000/API/{self.sexmex_category_path.replace(self.base_path,"")}/{video_name}.jpg'
                photo_url = self.find_element('photo url','video', By.TAG_NAME).get_attribute('poster')
                if photo_url:
                    response = requests.get(photo_url)
                    with open(os.path.join(self.sexmex_category_path, f'{video_name}.jpg'), 'wb') as f:
                        f.write(response.content)

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

                video_file = f'{self.sexmex_category_path}/{video_name}.mp4'
                if os.path.exists(video_file) :
                    video_file = self.copy_files_in_media_folder(video_file)
                    
                image_file = f'{self.sexmex_category_path}/{video_name}.jpg'
                if os.path.exists(image_file) :
                    image_file = self.copy_files_in_media_folder(image_file)
                    
                videos_data_obj = VideosData.objects.create(
                    video = video_file,
                    image = image_file,
                    Username = self.sexmex.username,
                    Likes = 0,
                    Disclike = 0,
                    Url = self.driver.current_url,
                    Title = video_title,
                    Discription = discription,
                    Release_Date = tmp["Release-Date"],
                    Poster_Image_url = tmp["Poster-Image_uri"],
                    video_download_url = tmp["poster_download_uri"],
                    Video_name = tmp["Video-name"],
                    Photo_name = tmp["Photo-name"],
                    Pornstarts = tmp["Pornstarts"],
                    configuration = self.sexmex
                )
                if self.sexmax.main_category :
                    cetegory_obj, _ = cetegory.objects.get_or_create(category = self.sexmax.main_category)
                    videos_data_obj.cetegory = cetegory_obj
                    videos_data_obj.save()
                    
            except :
                pass