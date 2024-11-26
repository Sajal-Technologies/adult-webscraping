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
                
                payload_captcha_img = os.path.join(os.getcwd(),"downloads/payload.jpeg")
                download_image(captcha_img_src,payload_captcha_img)
                
                all_td = self.driver.find_elements(By.TAG_NAME,'td')
                if len(all_td) == 9:
                    row= 3
                    col = 3
                else :
                    row = 4
                    col = 4
                
                result = solver.grid(file=payload_captcha_img,hintText = descriptions.text, rows=row, cols=col)
                    
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


        self.fivekteen = configuration.objects.get(website_name='Fivek_teen')
        self.fivekteen_category_path = self.create_or_check_path('fivekteen_category_videos')
        # Login process
        # self.driver_type = 'normal'

        self.get_driver()
        for i in range(2):

            self.driver.get('https://members.5kporn.com/')
            self.load_cookies(self.fivekteen.website_name, 'https://members.5kporn.com/')
            self.random_sleep()

            if self.find_element('Sign Out', "//button[contains(normalize-space(.), 'Logout')]"):
                self.driver.refresh()
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
        video_count = self.fivekteen.numbers_of_download_videos
        videos_urls = []
        df_url = [i.Url for i in VideosData.objects.filter(configuration = self.fivekteen )]

        page_count = 2
        successfully_downloaded_videos = 0
        while True:
            if video_count == successfully_downloaded_videos :
                break
            while True:
                self.driver.get('https://members.5kporn.com/?site=2')
                all_video = self.driver.find_elements(By.XPATH,'//*[@class="ep"]')
                
                for video in all_video:
                    date = video.find_element(By.XPATH, './div[1]/div[1]')
                    
                    today = datetime.now()
                    old_date = today - timedelta(days=self.fivekteen.more_than_old_days_download)
                    date_obj = parser.parse(date.text)
                    
                    if date_obj < old_date:
                        video_url = video.find_element(By.XPATH ,'./div[2]/div/a').get_attribute('href')
                        post_url = video.find_element(By.XPATH ,'./div[2]/div/a/div/img[1]').get_attribute('src')
                        if post_url and video_url not in df_url and (video_count - successfully_downloaded_videos) > len(videos_urls):
                            videos_urls.append({"video_url": video_url, 'post_url': post_url})
                        if (video_count - successfully_downloaded_videos) == len(videos_urls):
                            break
                if (video_count - successfully_downloaded_videos) == len(videos_urls):
                    break

                self.driver.get(f'https://members.5kporn.com/?site=2&page={page_count}')
                page_count+=1

            for item in videos_urls: 
                if video_count == successfully_downloaded_videos:
                    break
                
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
                tmp['video_download_url'] = f'http://208.122.217.49:8000/API/downloads/fivekteen_category_videos/{video_name}.mp4'
                tmp['poster_download_uri'] = f'http://208.122.217.49:8000/API/downloads/fivekteen_category_videos/{video_name}.jpg'
                tmp['Video-name'] = f'{video_name}.mp4'
                tmp['Photo-name'] = f'{video_name}.jpg'
                tmp['Pornstarts'] = self.find_element('pornstar', '//h5[contains(text(), "Starring:")]').text.split('Starring: ')[-1]
                tmp['Username'] = self.fivekteen.website_name
                self.click_element('download', '//*[@data-target="#download-modal"]')
                download_table = self.find_element('Download table','download-modal',By.ID)
                if download_table:
                    self.click_element('Best quality download video','//*[@id="collapseEPS"]/div/ul/li')
                name_of_file = tmp['Video-name']
                file_name = self.wait_for_file_download(timeout=600)
                if file_name == False :
                        [ os.remove(os.path.join(os.getcwd(),'downloads',i)) for i in os.listdir('downloads') if i.endswith('.crdownload') or i.endswith('.mp4') ]
                        continue
                    
                cetegory_obj, _ = cetegory.objects.get_or_create(category = "site1")
                
                media_path = os.path.join(os.getcwd(),'media')
                video_media_path = os.path.join(media_path,'videos','fivekteen_category_videos',cetegory_obj.category)
                image_media_path = os.path.join(media_path,'image','fivekteen_category_videos',cetegory_obj.category)
                
                os.makedirs(video_media_path, exist_ok=True)
                os.makedirs(image_media_path, exist_ok=True)
                
                final_video_media_path = os.path.join(video_media_path, tmp['Video-name'])
                os.rename(os.path.join(self.download_path,file_name), final_video_media_path)
                self.random_sleep(3,5)
                
                final_image_media_path = os.path.join(image_media_path,tmp["Video-name"].replace('.mp4','.jpg'))
                response = requests.get(tmp['Poster-Image_uri'])
                if response.status_code == 200:
                    with open(final_image_media_path, 'wb') as file: 
                        file.write(response.content)
                    
                object_video_file = os.path.join('image','fivekteen_category_videos',cetegory_obj.category,f'{tmp["Video-name"]}'.replace('.mp4','.jpg'))
                object_image_file = os.path.join('videos','fivekteen_category_videos',cetegory_obj.category,f'{tmp["Video-name"]}')
                    
                VideosData.objects.create(
                        video = object_video_file,
                        image = object_image_file,
                        Username = self.fivekteen.username,
                        Likes = 0,
                        Disclike = 0,
                        Url = self.driver.current_url,
                        Title = tmp["Title"],
                        Discription = tmp["Discription"],
                        Release_Date = tmp["Release-Date"],
                        Poster_Image_url = tmp["Poster-Image_uri"],
                        Video_name = tmp["Video-name"],
                        Photo_name = tmp["Photo-name"],
                        Pornstarts = tmp["Pornstarts"],
                        configuration = self.fivekteen,
                        cetegory = cetegory_obj
                    )
                
                successfully_downloaded_videos += 1
                    
    def download_fivek_porn_video(self):
        video_count = self.fivekteen.numbers_of_download_videos

        csv_name = '5kporn'
        videos_urls = []

        df_url = [i.Url for i in VideosData.objects.filter(configuration = self.fivekteen )]
        page_count = 2

        
        successfully_downloaded_videos = 0
        while True:
            if video_count == successfully_downloaded_videos :
                break
            while True:
                
                self.driver.get('https://members.5kporn.com/?site=1')
                all_video = self.driver.find_elements(By.XPATH,'//*[@class="ep"]')
                
                for video in all_video:
                    date = video.find_element(By.XPATH, './div[1]/div[1]')
                    if self.date_older_or_not(date.text):
                        video_url = video.find_element(By.XPATH ,'./div[2]/div/a').get_attribute('href')
                        post_url = video.find_element(By.XPATH ,'./div[2]/div/a/div/img[1]').get_attribute('src')
                        if post_url and video_url not in df_url and (video_count - successfully_downloaded_videos) > len(videos_urls):
                            videos_urls.append({"video_url": video_url, 'post_url': post_url})
                            
                        if (video_count - successfully_downloaded_videos) == len(videos_urls):
                            break
                        
                if (video_count - successfully_downloaded_videos) == len(videos_urls):
                    break

                self.driver.get(f'https://members.5kporn.com/?site=1&page={page_count}')
                page_count+=1

            for item in videos_urls:
                if video_count == successfully_downloaded_videos:
                    break
                
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
                tmp['video_download_url'] = f'http://208.122.217.49:8000/API/downloads/fivekteen_category_videos/{video_name}.mp4'
                tmp['poster_download_uri'] = f'http://208.122.217.49:8000/API/downloads/fivekteen_category_videos/{video_name}.jpg'
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
                if file_name == False :
                    [ os.remove(os.path.join(os.getcwd(),'downloads',i)) for i in os.listdir('downloads') if i.endswith('.crdownload') or i.endswith('.mp4') ]
                    continue
                
                cetegory_obj, _ = cetegory.objects.get_or_create(category = "site1")
                
                media_path = os.path.join(os.getcwd(),'media')
                video_media_path = os.path.join(media_path,'videos','fivekteen_category_videos',cetegory_obj.category)
                image_media_path = os.path.join(media_path,'image','fivekteen_category_videos',cetegory_obj.category)
                
                os.makedirs(video_media_path, exist_ok=True)
                os.makedirs(image_media_path, exist_ok=True)
                
                final_video_media_path = os.path.join(video_media_path, tmp['Video-name'])
                os.rename(os.path.join(self.download_path,file_name), final_video_media_path)
                self.random_sleep(3,5)
                
                final_image_media_path = os.path.join(image_media_path,tmp["Video-name"].replace('.mp4','.jpg'))
                response = requests.get(tmp['Poster-Image_uri'])
                if response.status_code == 200:
                    with open(final_image_media_path, 'wb') as file: 
                        file.write(response.content)
                    
                object_video_file = os.path.join('image','fivekteen_category_videos',cetegory_obj.category,f'{tmp["Video-name"]}'.replace('.mp4','.jpg'))
                object_image_file = os.path.join('videos','fivekteen_category_videos',cetegory_obj.category,f'{tmp["Video-name"]}')
                
                if os.path.exists(final_video_media_path) and os.path.exists(final_image_media_path) :
                
                    VideosData.objects.create(
                            video = object_video_file,
                            image = object_image_file,
                            Username = self.fivekteen.username,
                            Likes = 0,
                            Disclike = 0,
                            Url = self.driver.current_url,
                            Title = tmp["Title"],
                            Discription = tmp["Discription"],
                            Release_Date = tmp["Release-Date"],
                            Poster_Image_url = tmp["Poster-Image_uri"],
                            Video_name = tmp["Video-name"],
                            Photo_name = tmp["Photo-name"],
                            Pornstarts = tmp["Pornstarts"],
                            configuration = self.fivekteen,
                            cetegory = cetegory_obj
                        )
                    
                    successfully_downloaded_videos += 1