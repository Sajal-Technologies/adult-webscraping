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


class Bot(StartDriver):
    
    def whorny_login(self):
        ''' 
        This function automates the login process for the WhornyFilms  website.

        Returns:
            bool: True if login is successful, False otherwise.
        '''
        
        # Login process
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
    
    def download_whorny_videos(self):
        videos_urls = 0
        self.random_sleep(3,5)
        df_url = [i.Url for i in VideosData.objects.filter(configuration=self.whorny)]
        max_video = self.whorny.numbers_of_download_videos
        collection_name = 'whornyfilms_videos'
        collection_path = self.create_or_check_path(self.whorny_category_path, sub_folder_=collection_name)
        
        while videos_urls < max_video:
            self.driver.get('https://members.whornyfilms.com/search-and-filter/')
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
                        if date and self.date_older_or_not(date,self.whorny.more_than_old_days_download):
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
                                

                                media_path = os.path.join(os.getcwd(),'media')
                                video_media_path = os.path.join(media_path,'videos','Whorny_category_videos',"collection_name")
                                image_media_path = os.path.join(media_path,'image','Whorny_category_videos',"collection_name")

                                os.makedirs(video_media_path, exist_ok=True)
                                os.makedirs(image_media_path, exist_ok=True)
                                
                                final_video_media_path = os.path.join(video_media_path,f'{video_name}.mp4')
                                final_image_media_path = os.path.join(image_media_path,f'{video_name}.jpg')
                                
                                response = requests.request("GET", post_url, headers=headers, data=payload)
                                with open(final_image_media_path, 'wb') as file:
                                    file.write(response.content)
                                    
                                self.click_element('download button', '//*[@data-id="dd55478"]')
                                url = self.find_element('download button', '//*[@data-id="1a4b7e6"]').find_element(By.TAG_NAME, 'a').get_attribute('href')
                                headers = {
                                    'Referer': 'https://downloads.whornyfilms.com/', 
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',                                'Accept-Encoding': 'gzip, deflate, br, zstd',                               
                                    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                                    }
                                self.download_video_from_request(url, final_video_media_path, headers)
                                
                                
                                object_video_file = os.path.join('videos','sexmex_category_videos',self.whorny.main_category,f'{video_name}.mp4')
                                object_image_file = os.path.join('image','sexmex_category_videos',self.whorny.main_category,f'{video_name}.jpg')
                                print("Image file : ",object_image_file)
                                print("Video file : ",object_video_file)
                                
                                if os.path.exists(final_video_media_path) and os.path.exists(final_image_media_path) :
                                    
                                    videos_data_obj = VideosData.objects.create(
                                        Username = self.whorny.username,
                                        Likes = 0,
                                        Disclike = 0,
                                        Url = self.driver.current_url,
                                        Title = tmp['Title'],
                                        Discription = tmp['Discription'],
                                        Release_Date = tmp["Release-Date"],
                                        Poster_Image_url = tmp["Poster-Image_uri"],
                                        Video_name = tmp["Video-name"],
                                        Photo_name = tmp["Photo-name"],
                                        Pornstarts = tmp["Pornstarts"],
                                        configuration = self.whorny
                                    )
                                    
                                    if self.whorny.main_category :
                                        cetegory_obj, _ = cetegory.objects.get_or_create(category = self.whorny.main_category)
                                        if cetegory_obj not in self.whorny.category.all():
                                            self.whorny.category.add(cetegory_obj)
                                        videos_data_obj.cetegory = cetegory_obj
                                        videos_data_obj.save()
                                    
                                    if os.path.exists(final_video_media_path) and os.path.exists(final_image_media_path) :
                                        videos_data_obj.video = object_video_file
                                        videos_data_obj.image = object_image_file
                                        videos_data_obj.save()
                                    else :
                                        videos_data_obj.delete()
                                videos_urls+=1
                            except:
                                continue
            # Go to the next page if available
            self.driver.get('https://members.whornyfilms.com/search-and-filter/')
            next_btn = self.click_element('next', '//*[@class="dce-pagination"]')
            if not next_btn:break