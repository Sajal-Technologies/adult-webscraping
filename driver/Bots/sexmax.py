from numpy import delete
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
        if self.sexmex.main_category :
            self.sexmex_category_path = self.create_or_check_path(self.sexmex_category_path,sub_folder_=self.sexmex.main_category)
        
        df_url = [i.Url for i in VideosData.objects.filter(configuration=self.sexmex)]
        
        max_video = self.sexmex.numbers_of_download_videos
        found_videos = 0

        video_list = []
        self.random_sleep(4,7,reson="to let load the html of home page")
        self.click_element('see more', 'float-end', By.CLASS_NAME)
        self.driver.get('https://members.sexmex.xxx/members/category.php?id=5')

        current_date = datetime.now()
        while found_videos < max_video:
            section = self.find_element('section', '/html/body/div[3]/div[1]')
            all_div = section.find_elements(By.XPATH, './div')
            for div in all_div:
                scene_date = div.find_element(By.CLASS_NAME, 'scene-date').text
                
                given_date = datetime.strptime(scene_date, '%m/%d/%Y')
                date_difference = current_date - given_date

                if date_difference > timedelta(days=self.sexmex.more_than_old_days_download):
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
                photo_url = ""
                photo_url = self.find_element('photo url','video', By.TAG_NAME).get_attribute('poster') 
                
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
                                 
                media_path = os.path.join(os.getcwd(),'media')
                video_media_path = os.path.join(media_path,'videos','sexmex_category_videos',self.sexmex.main_category)
                image_media_path = os.path.join(media_path,'image','sexmex_category_videos',self.sexmex.main_category)

                os.makedirs(video_media_path, exist_ok=True)
                os.makedirs(image_media_path, exist_ok=True)
                
                final_video_media_path = os.path.join(video_media_path,f'{video_name}.mp4')
                final_image_media_path = os.path.join(image_media_path,f'{video_name}.jpg')
                
                if not photo_url :
                    photo_url = self.find_element('photo url','video', By.TAG_NAME).get_attribute('poster') 
                if photo_url:
                    response = requests.get(photo_url)
                    with open(final_image_media_path, 'wb') as f: 
                        f.write(response.content)
                
                video_url = self.find_element('video url', '//*[text()="1080p"]').get_attribute('value')
                self.download_video_from_request(video_url, final_video_media_path)
                
               

                object_video_file = os.path.join('videos','sexmex_category_videos',self.sexmex.main_category,f'{video_name}.mp4')
                object_image_file = os.path.join('image','sexmex_category_videos',self.sexmex.main_category,f'{video_name}.jpg')
                print("Image file : ",object_image_file)
                print("Video file : ",object_video_file)

                
                
                videos_data_obj = VideosData.objects.create(
                    Username = self.sexmex.username,
                    Likes = 0,
                    Disclike = 0,
                    Url = self.driver.current_url,
                    Title = video_title,
                    Discription = discription,
                    Release_Date = tmp["Release-Date"],
                    Poster_Image_url = tmp["Poster-Image_uri"],
                    Video_name = tmp["Video-name"],
                    Photo_name = tmp["Photo-name"],
                    Pornstarts = tmp["Pornstarts"],
                    configuration = self.sexmex
                )
                if self.sexmex.main_category :
                    cetegory_obj, _ = cetegory.objects.get_or_create(category = self.sexmex.main_category)
                    if cetegory_obj not in self.sexmex.category.all():
                        self.sexmex.category.add(cetegory_obj)
                    videos_data_obj.cetegory = cetegory_obj
                    videos_data_obj.save()
                
                if os.path.exists(final_video_media_path) and os.path.exists(final_image_media_path) :
                    videos_data_obj.video = object_video_file
                    videos_data_obj.image = object_image_file
                    videos_data_obj.save()
                else :
                    videos_data_obj.delete()
                    
            except :
                pass