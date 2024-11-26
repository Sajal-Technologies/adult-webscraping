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
from anticaptchaofficial.imagecaptcha import *



class Bot(StartDriver):
    
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

        for i in range(2):
            self.driver.get('https://adultprime.com/loginav')
            self.load_cookies(self.adultprime.website_name)
            self.driver.refresh()
            if self.find_element('Sign Out', '//*[text()="Sign Out"]'):
                return True

            self.click_element('confirm', "confirm-btn", By.ID)
            if not self.click_element('login btn', '//*[@class="login-menu-btn"]'):
                self.driver.get('https://adultprime.com/loginav')
                
            self.input_text(self.adultprime.username, 'username_input', '//*[@id="login-form-main"]//*[@id="LoginForm_username"]')
            self.input_text(self.adultprime.password, 'password_input','//*[@id="login-form-main"]//*[@id="LoginForm_password"]')

            for i in range(3):
                self.click_element('refresh captcha', '//*[@id="yw0_button"]')
                self.random_sleep(1,2)
                img = self.find_element('links','//*[@id="yw0"]')
                captcha = img.screenshot_as_png
                self.random_sleep(2,3)
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
                if self.adultprime.main_category.lower() in i.text.lower():
                    self.ensure_click(i)
                    self.random_sleep(2,3)
                    if self.driver.current_url != 'https://adultprime.com/categories':
                        link_element = self.find_element('view all', '//*[@class="pull-right link-all"]/a[contains(@href, "videos")]')
                        link = link_element.get_attribute('href')
                        if link: self.driver.get(link)
                        else:
                            self.driver.get(f'https://adultprime.com/studios/search?q={self.adultprime.main_category}')
                            link_element = self.find_element('view all', '//*[@class="pull-right link-all"]/a[contains(@href, "videos")]')
                            link = link_element.get_attribute('href')
                            if link: self.driver.get(link)
                            else:
                                SendAnEmail(f"We don't find this {self.adultprime.main_category} category")
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
        for category in self.adultprime.category.all() : 
            if category.link :
                url = category.link
                self.category = category
            else :
                url = f'https://adultprime.com/studios/videos?website={category}'
                
            videos_dict = self.adultprime_get_video(url, True)
            self.adultprime_download_video(videos_dict)

    def adultprime_get_video(self, url:str='', channel:bool=False):
        '''
        Parameter :
        url:str = Default is empty str, channel's url or anyother url of aDultprime website
        channel: bool = Default is False, if url is channels url than make this True
        '''
        
        video_detailes = {'collection_name':'','video_list':[]}
        videos_urls = []
        if channel: self.driver.get(url)
        else:
            if not self.get_adultprime_category(): 
                return None
            
        self.random_sleep(3,5)
        df_url = [i.Url for i in VideosData.objects.filter(configuration = self.adultprime )]
        max_video = self.adultprime.numbers_of_download_videos
        while len(videos_urls) < max_video:
            row_element = self.find_element('row', "//div[@class='row portal-grid']")
            li_tags = row_element.find_elements(By.CSS_SELECTOR, ".model-wrapper.portal-video-wrapper")

            for i, li_tag in enumerate(li_tags, start=1):
                # Get video date and check if it's old
                all_timestamp = li_tag.find_element(By.XPATH,'.//span[@class="description-releasedate"]')
                video_date = all_timestamp.get_attribute("innerHTML").replace('<i class="fa fa-calendar"></i> ',"")
                video_url = li_tag.find_element(By.CSS_SELECTOR, "a[href^='/studios/video']")
                today = datetime.now()
                old_date = today - timedelta(days=self.adultprime.more_than_old_days_download)
                date_obj = parser.parse(video_date)
                
                if video_date and date_obj < old_date:
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

                Title = self.find_element('Title','//div[@class=" video-title-container"]')
                if Title :
                    MainTitle = Title.find_element(By.TAG_NAME,'h1')
                    if MainTitle :
                        tmp['Title'] = MainTitle.text

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
                
                self.click_element('download drop menu','//*[@id="theatre-row"]/div[1]/div[2]/div/div[2]/div/div[1]/button')
                
                DownloadQualityMenu = self.driver.find_element(By.XPATH, '//ul[@class="dropdown-menu btn-block"]')
                FullHD_link = DownloadQualityMenu.find_elements(By.TAG_NAME,'li')
                
                videos_data_obj = VideosData.objects.create(
                    Username = self.adultprime.username,
                    Likes = tmp['Likes'],
                    Disclike = tmp['Disclike'],
                    Url = tmp['Url'],
                    Title = tmp["Title"],
                    Discription = tmp["Discription"],
                    Release_Date = tmp["Release-Date"],
                    Poster_Image_url = tmp["Poster-Image_uri"],
                    video_download_url = tmp["poster_download_uri"],
                    Video_name = tmp["Video-name"],
                    Photo_name = tmp["Photo-name"],
                    Pornstarts = tmp["Pornstarts"],
                    configuration = self.adultprime
                )
                if self.category :
                    cetegory_obj, _ = cetegory.objects.get_or_create(category = self.category)
                    videos_data_obj.cetegory = cetegory_obj
                    videos_data_obj.save()
                
                if len(FullHD_link) > 2:
                    decoded_url = FullHD_link[2].find_element(By.TAG_NAME,'a')
                    decoded_url.click()
                    self.random_sleep(2,3)
                    
                    # video_url = self.find_element('video url', '//*[text()="1080p"]').get_attribute('value')
                    # self.download_video_from_request(video_url, os.path.join(self.sexmex_category_path, f'{video_name}.mp4'))

                    video_file = f'{self.adultprime_category_path}/{video_name}.mp4'
                    if os.path.exists(video_file) :
                        video_file = self.copy_files_in_media_folder(video_file)
                        if video_file :
                            videos_data_obj.video = video_file
                            
                        
                    image_file = f'{self.adultprime_category_path}/{video_name}.jpg'
                    if os.path.exists(image_file) :
                        image_file = self.copy_files_in_media_folder(image_file,folder="image")
                        if image_file :
                            videos_data_obj.image = image_file
                    
                    videos_data_obj.save()
                    # self.download_video_from_request(decoded_url, local_filename)
                else:continue

                
            except Exception as e:
                print('Error:', e)