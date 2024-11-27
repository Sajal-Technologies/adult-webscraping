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
    
    def revsharecash_download(self):
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
            
            if website == 'underwatershow':
                self.underwatershow_videos_download(website,url)
            else:
                self.videos_download(website, url)
                
    def videos_download(self,website="", website_url=None):
        if not website : return 
        if not website_url : return 
        
        self.driver.get(website_url)

        self.check_csv_exist(self.csv_name)
        
        website_name = website
        csv_name = self.csv_name

        collection_name = f'{website}_videos'
        collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_=f'{website}_videos')


        df_url = [i.Url for i in VideosData.objects.filter(configuration=self.revsharecash)]

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

            if not videos_url :
                all_block = self.driver.find_elements(By.CLASS_NAME, "one_video_block")
                for block in all_block: 
                    all_thumb = block.find_elements(By.CLASS_NAME, 'one_video_block_content')
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

                    
                    media_path = os.path.join(os.getcwd(),'media')
                    video_media_path = os.path.join(media_path,'videos','revsharecash_category_videos',website)
                    image_media_path = os.path.join(media_path,'image','revsharecash_category_videos',website)

                    os.makedirs(video_media_path, exist_ok=True)
                    os.makedirs(image_media_path, exist_ok=True)
                    
                    # download image
                    response = requests.get(tmp['Poster-Image_uri'])
                    final_image_media_path = os.path.join(image_media_path,f'{video_name}.jpg')
                    if response.status_code == 200:
                        with open(final_image_media_path, 'wb') as file: file.write(response.content)
       
                    # download video
                    final_video_media_path = os.path.join(video_media_path,f'{video_name}.mp4')
                    url = self.driver.find_elements(By.XPATH, '//a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
                    self.download_video_from_request(url,final_video_media_path)
                    
                    object_video_file = os.path.join('videos','revsharecash_category_videos',website,f'{video_name}.mp4')
                    object_image_file = os.path.join('image','revsharecash_category_videos',website,f'{video_name}.jpg')
                    print("Image file : ",object_image_file)
                    print("Video file : ",object_video_file)
                
                    cetegory_obj, _ = cetegory.objects.get_or_create(category = website)
                    
                    if cetegory_obj not in self.revsharecash.category.all():
                        self.revsharecash.category.add(cetegory_obj)
                        
                    videos_data_obj = VideosData.objects.create(
                            video = object_video_file,
                            image = object_image_file,
                            Username = self.revsharecash.username,
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
                            configuration = self.revsharecash,
                            cetegory = cetegory_obj
                        )
                    
                    found_videos+=1

            if not found_videos >= max_video:
                # pagignation
                self.driver.save_screenshot("driver.png")
                self.driver.get(website_url)
                self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
                website_url = self.driver.current_url
                
                
    def underwatershow_videos_download(self,website, website_url=None):
        if not website : return 
        if not website_url : return 
        
        self.driver.get(website_url)

        self.check_csv_exist(self.csv_name)
        
        website_name = website
        csv_name = self.csv_name

        collection_name = f'{website}_videos'
        collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_=f'{website}_videos')

        df_url = [i.Url for i in VideosData.objects.filter(configuration=self.revsharecash)]

        max_video = self.revsharecash.numbers_of_download_videos
        found_videos = 0

        while found_videos < max_video:
            
            
            
            # get all videos link
            videos_url = []
            all_block = self.driver.find_elements(By.CLASS_NAME, "one_video_block")
            for block in all_block: 
                if found_videos >= max_video:
                    break
                
                all_thumb = block.find_elements(By.CLASS_NAME, 'one_video_block_content')
                for thumb in all_thumb: 
                    url = thumb.find_elements(By.XPATH, './/a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
                    videos_url.append([block, url])
                    
            for videos_ele in videos_url:
                if found_videos >= max_video:
                    break
                
                block = videos_ele[0]
                url = videos_ele[-1]
                
                title = block.find_element(By.CLASS_NAME, 'video_title1').text.split('(')[0].strip()
                video_name = f"{collection_name.replace('_videos', '')}_{self.sanitize_title(title)}"
                # video_footer
                galary_url = block.find_elements(By.XPATH, './/a[contains(@href, "/members/gal")]')
                if galary_url :
                    galary_url = galary_url[0].get_attribute('href')
                else:
                    galary_url = f"https://underwatershow.com/members/gal/{title}".lower()
                
                image_src = block.find_elements(By.TAG_NAME, 'img')
                if image_src :
                    image_src = image_src[0].get_attribute('src')
                else:
                    image_src = ""
                
                block.find_elements(By.TAG_NAME, 'img')
                tmp = {}
                tmp['Title'] = title
                tmp['Discription'] = "Not available"
                tmp['Release-Date'] = "Not available"
                tmp['Likes'] = "Not available"
                tmp['Disclike'] = "Not available"
                tmp['Url'] = galary_url
                tmp['Poster-Image_uri'] = image_src
                tmp['Category'] = website_name
                tmp['video_download_url'] = f"http://208.122.217.49:8000/API/media/download/videos{collection_path.split('downloads')[-1]}/{video_name}.mp4/"
                tmp['poster_download_uri'] = f"http://208.122.217.49:8000/API/media/download/image{collection_path.split('downloads')[-1]}/{video_name}.jpg/"
                tmp['Video-name'] = f'{video_name}.mp4'
                tmp['Photo-name'] = f'{video_name}.jpg'
                tmp['Pornstarts'] = "Not available"
                tmp['Username'] = self.revsharecash.website_name

                #  class for get url of video video_footer
                media_path = os.path.join(os.getcwd(),'media')
                video_media_path = os.path.join(media_path,'videos','revsharecash_category_videos',website)
                image_media_path = os.path.join(media_path,'image','revsharecash_category_videos',website)

                os.makedirs(video_media_path, exist_ok=True)
                os.makedirs(image_media_path, exist_ok=True)
                
                # download image
                response = requests.get(tmp['Poster-Image_uri'])
                final_image_media_path = os.path.join(image_media_path,f'{video_name}.jpg')
                if response.status_code == 200:
                    with open(final_image_media_path, 'wb') as file: file.write(response.content)
    
                # download video
                final_video_media_path = os.path.join(video_media_path,f'{video_name}.mp4')
                self.download_video_from_request(url,final_video_media_path)
                
                object_video_file = os.path.join('videos','revsharecash_category_videos',website,f'{video_name}.mp4')
                object_image_file = os.path.join('image','revsharecash_category_videos',website,f'{video_name}.jpg')
                print("Image file : ",object_image_file)
                print("Video file : ",object_video_file)
            
                cetegory_obj, _ = cetegory.objects.get_or_create(category = website)
                
                if cetegory_obj not in self.revsharecash.category.all():
                        self.revsharecash.category.add(cetegory_obj)
                        
                videos_data_obj = VideosData.objects.create(
                        video = object_video_file,
                        image = object_image_file,
                        Username = self.revsharecash.username,
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
                        configuration = self.revsharecash,
                        cetegory = cetegory_obj
                    )
                
                found_videos+=1

            if not found_videos >= max_video:
                # pagignation
                self.driver.get(website_url)
                self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
                website_url = self.driver.current_url
                
                       
    # def defloration_videos_download(self, website_url=None):
    #     self.driver.get(website_url)

    #     self.check_csv_exist(self.csv_name)
        
    #     website_name = 'defloration'
    #     csv_name = self.csv_name

    #     collection_name = 'defloration_videos'
    #     collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_='defloration_videos')


    #     df_url = [i.Url for i in VideosData.objects.filter(configuration=self.revsharecash)]

    #     max_video = self.revsharecash.numbers_of_download_videos
    #     found_videos = 0

    #     while found_videos < max_video:

    #         # get all videos link
    #         videos_url = []
    #         all_block = self.driver.find_elements(By.CLASS_NAME, "images_block_content")
    #         for block in all_block:
    #             all_thumb = block.find_elements(By.CLASS_NAME, 'thumb_block')
    #             for thumb in all_thumb:
    #                 videos_url.append(thumb.find_element(By.TAG_NAME, 'a').get_attribute('href'))

    #         # scraping and download process
    #         for url in videos_url:
    #             if found_videos == max_video:
    #                 break
    #             if url not in df_url:
    #                 self.driver.get(url)
    #                 video_block = self.driver.find_element(By.CLASS_NAME, "one_video_block")

    #                 title = video_block.find_element(By.CLASS_NAME, 'video_title').text.split('(')[0].strip()
    #                 video_name = f"{collection_name.replace('_videos', '')}_{url.split('/')[-1]}_{self.sanitize_title(title)}"
                    
    #                 tmp = {}
    #                 tmp['Title'] = title
    #                 tmp['Discription'] = "Not available"
    #                 tmp['Release-Date'] = "Not available"
    #                 tmp['Likes'] = "Not available"
    #                 tmp['Disclike'] = "Not available"
    #                 tmp['Url'] = self.driver.current_url
    #                 tmp['Poster-Image_uri'] = self.driver.find_element(By.CLASS_NAME, "video_screenshot").get_attribute('src')
    #                 tmp['Category'] = website_name
    #                 tmp['video_download_url'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
    #                 tmp['poster_download_uri'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
    #                 tmp['Video-name'] = f'{video_name}.mp4'
    #                 tmp['Photo-name'] = f'{video_name}.jpg'
    #                 tmp['Pornstarts'] = "Not available"
    #                 tmp['Username'] = self.revsharecash.website_name

                    
    #                 media_path = os.path.join(os.getcwd(),'media')
    #                 video_media_path = os.path.join(media_path,'videos','revsharecash_category_videos',self.revsharecash)
    #                 image_media_path = os.path.join(media_path,'image','revsharecash_category_videos',self.revsharecash)
            
    #                 response = requests.get(tmp['Poster-Image_uri'])
    #                 image_file_path = os.path.join(collection_path, f'{video_name}.jpg')
    #                 with open(image_file_path, 'wb') as file:
    #                     file.write(response.content)
    #                 image_file_path = self.copy_files_in_media_folder(image_file_path)
                        

    #                 url = self.driver.find_elements(By.XPATH, '//a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
    #                 video_file_path = os.path.join(collection_path, tmp['Video-name'])
    #                 self.download_video_from_request(url,video_file_path)
    #                 video_file_path = self.copy_files_in_media_folder(video_file_path)
                    
    #                 cetegory_obj, _ = cetegory.objects.get_or_create(category = "defloration")
    #                 videos_data_obj = VideosData.objects.create(
    #                         video = video_file_path,
    #                         image = image_file_path,
    #                         Username = self.revsharecash.username,
    #                         Likes = 0,
    #                         Disclike = 0,
    #                         Url = self.driver.current_url,
    #                         Title = tmp["Title"],
    #                         Discription = tmp["Discription"],
    #                         Release_Date = tmp["Release-Date"],
    #                         Poster_Image_url = tmp["Poster-Image_uri"],
    #                         Video_name = tmp["Video-name"],
    #                         Photo_name = tmp["Photo-name"],
    #                         Pornstarts = tmp["Pornstarts"],
    #                         configuration = self.revsharecash,
    #                         cetegory = cetegory_obj
    #                     )
                    
                    
    #                 found_videos+=1


    #         if not found_videos >= max_video:
    #             # pagignation
    #             self.driver.get(website_url)
    #             self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
    #             website_url = self.driver.current_url


    # def flexyteens_videos_download(self, website_url=None):
    #     self.driver.get(website_url)

    #     website_name = 'flexyteens'
    #     csv_name = 'revsharecash_flexyteens'

    #     collection_name = 'flexyteens_videos'
    #     collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_='flexyteens_videos')

    #     self.make_csv(csv_name, new=True)
    #     df_url = self.column_to_list(csv_name,'Url')

    #     max_video = self.revsharecash.numbers_of_download_videos
    #     found_videos = 0

    #     while found_videos < max_video:

    #         # get all videos link
    #         videos_url = []
    #         all_block = self.driver.find_elements(By.CLASS_NAME, "images_block_content")
    #         for block in all_block:
    #             all_thumb = block.find_elements(By.CLASS_NAME, 'thumb_block')
    #             for thumb in all_thumb:
    #                 videos_url.append(thumb.find_element(By.TAG_NAME, 'a').get_attribute('href'))

    #         # scraping and download process
    #         for url in videos_url:
    #             if found_videos >= max_video:
    #                 break
    #             if url not in df_url:
    #                 self.driver.get(url)
    #                 video_block = self.driver.find_element(By.CLASS_NAME, "one_video_block")

    #                 title = video_block.find_element(By.CLASS_NAME, 'video_title').text.split('(')[0].strip()
    #                 video_name = f"{collection_name.replace('_videos', '')}_{url.split('/')[-1]}_{self.sanitize_title(title)}"

    #                 tmp = {}
    #                 tmp['Title'] = title
    #                 tmp['Discription'] = "Not available"
    #                 tmp['Release-Date'] = "Not available"
    #                 tmp['Likes'] = "Not available"
    #                 tmp['Disclike'] = "Not available"
    #                 tmp['Url'] = self.driver.current_url
    #                 tmp['Poster-Image_uri'] = self.driver.find_element(By.CLASS_NAME, "video_screenshot").get_attribute('src')
    #                 tmp['Category'] = website_name
    #                 tmp['video_download_url'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
    #                 tmp['poster_download_uri'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
    #                 tmp['Video-name'] = f'{video_name}.mp4'
    #                 tmp['Photo-name'] = f'{video_name}.jpg'
    #                 tmp['Pornstarts'] = "Not available"
    #                 tmp['Username'] = self.revsharecash.website_name

    #                 response = requests.get(tmp['Poster-Image_uri'])
    #                 image_file_path = os.path.join(collection_path, f'{video_name}.jpg')
    #                 with open(image_file_path, 'wb') as file:
    #                     file.write(response.content)
    #                 image_file_path = self.copy_files_in_media_folder(image_file_path)
                        

    #                 url = self.driver.find_elements(By.XPATH, '//a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
    #                 video_file_path = os.path.join(collection_path, tmp['Video-name'])
    #                 self.download_video_from_request(url,video_file_path)
    #                 video_file_path = self.copy_files_in_media_folder(video_file_path)
                    
    #                 cetegory_obj, _ = cetegory.objects.get_or_create(category = "defloration")
    #                 videos_data_obj = VideosData.objects.create(
    #                         video = video_file_path,
    #                         image = image_file_path,
    #                         Username = self.revsharecash.username,
    #                         Likes = 0,
    #                         Disclike = 0,
    #                         Url = self.driver.current_url,
    #                         Title = tmp["Title"],
    #                         Discription = tmp["Discription"],
    #                         Release_Date = tmp["Release-Date"],
    #                         Poster_Image_url = tmp["Poster-Image_uri"],
    #                         Video_name = tmp["Video-name"],
    #                         Photo_name = tmp["Photo-name"],
    #                         Pornstarts = tmp["Pornstarts"],
    #                         configuration = self.revsharecash,
    #                         cetegory = cetegory_obj
    #                     )
    #                 found_videos += 1


    #         if not found_videos >= max_video:
    #             # pagignation
    #             self.driver.get(website_url)
    #             self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
    #             website_url = self.driver.current_url

    # def virginmassage_videos_download(self, website_url=None):
    #     self.driver.get(website_url)

    #     website_name = 'virginmassage'
    #     csv_name = 'revsharecash_virginmassage'

    #     collection_name = 'virginmassage_videos'
    #     collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_='virginmassage_videos')

    #     self.make_csv(csv_name, new=True)
    #     df_url = self.column_to_list(csv_name,'Url')

    #     max_video = self.revsharecash.numbers_of_download_videos
    #     found_videos = 0

    #     while found_videos < max_video:

    #         # get all videos link, scraping and download process
    #         all_block = self.driver.find_elements(By.CLASS_NAME, "one_video_block")
    #         for block in all_block:
    #             if found_videos >= max_video:
    #                 break
                
    #             video_url = block.find_element(By.CLASS_NAME, "one_video_block_content").find_element(By.TAG_NAME,'a').get_attribute('href')
    #             if video_url not in df_url:
    #                 title = block.find_element(By.CLASS_NAME, 'video_title1').text.split('(')[0].strip()
    #                 video_name = f"{collection_name.replace('_videos', '')}_{video_url.split('/')[-1]}_{self.sanitize_title(title)}"

    #                 tmp = {}
    #                 tmp['Title'] = title
    #                 tmp['Discription'] = "Not available"
    #                 tmp['Release-Date'] = "Not available"
    #                 tmp['Likes'] = "Not available"
    #                 tmp['Disclike'] = "Not available"
    #                 tmp['Url'] = video_url
    #                 tmp['Poster-Image_uri'] = block.find_element(By.CLASS_NAME, "video_screenshot").get_attribute('src')
    #                 tmp['Category'] = website_name
    #                 tmp['video_download_url'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
    #                 tmp['poster_download_uri'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
    #                 tmp['Video-name'] = f'{video_name}.mp4'
    #                 tmp['Photo-name'] = f'{video_name}.jpg'
    #                 tmp['Pornstarts'] = "Not available"
    #                 tmp['Username'] = self.revsharecash.website_name

    #                 response = requests.get(tmp['Poster-Image_uri'])
    #                 image_file_path = os.path.join(collection_path, f'{video_name}.jpg')
    #                 with open(image_file_path, 'wb') as file:
    #                     file.write(response.content)
    #                 image_file_path = self.copy_files_in_media_folder(image_file_path)
                        

    #                 url = self.driver.find_elements(By.XPATH, '//a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
    #                 video_file_path = os.path.join(collection_path, tmp['Video-name'])
    #                 self.download_video_from_request(url,video_file_path)
    #                 video_file_path = self.copy_files_in_media_folder(video_file_path)
                    
    #                 cetegory_obj, _ = cetegory.objects.get_or_create(category = "defloration")
    #                 videos_data_obj = VideosData.objects.create(
    #                         video = video_file_path,
    #                         image = image_file_path,
    #                         Username = self.revsharecash.username,
    #                         Likes = 0,
    #                         Disclike = 0,
    #                         Url = self.driver.current_url,
    #                         Title = tmp["Title"],
    #                         Discription = tmp["Discription"],
    #                         Release_Date = tmp["Release-Date"],
    #                         Poster_Image_url = tmp["Poster-Image_uri"],
    #                         Video_name = tmp["Video-name"],
    #                         Photo_name = tmp["Photo-name"],
    #                         Pornstarts = tmp["Pornstarts"],
    #                         configuration = self.revsharecash,
    #                         cetegory = cetegory_obj
    #                     )
    #                 found_videos += 1

    #         if not found_videos >= max_video:
    #             # pagignation
    #             self.driver.get(website_url)
    #             self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
    #             website_url = self.driver.current_url
    
    # def underwatershow_videos_download(self, website_url=None):
    #     # try:
    #         self.driver.get(website_url)

    #         website_name = 'underwatershow'
    #         csv_name = 'revsharecash_underwatershow'

    #         collection_name = 'underwatershow_videos'
    #         collection_path = self.create_or_check_path(self.revsharecash_category_path, sub_folder_='underwatershow_videos')

    #         self.make_csv(csv_name, new=True)
    #         df_url = self.column_to_list(csv_name,'Url')

    #         max_video = self.revsharecash.numbers_of_download_videos
    #         found_videos = 0

    #         while found_videos < max_video:

    #             # get all videos link, scraping and download process
    #             all_block = self.driver.find_elements(By.CLASS_NAME, "one_video_block")
    #             for block in all_block:
    #                 if found_videos >= max_video:
    #                     break
    #                 print(block.text)
    #                 video_url_dd = block.find_element(By.CLASS_NAME, "video_footer")
    #                 if str(video_url_dd.text).strip() == "":
    #                     continue
    #                 video_url = video_url_dd.find_element(By.TAG_NAME,'a').get_attribute('href')
    #                 if video_url not in df_url:

    #                     title = block.find_element(By.CLASS_NAME, 'video_title1').text.split('(')[0].strip()
    #                     video_name = f"{collection_name.replace('_videos', '')}_{video_url.split('/')[-1]}_{self.sanitize_title(title)}"

    #                     tmp = {}
    #                     tmp['Title'] = title
    #                     tmp['Discription'] = "Not available"
    #                     tmp['Release-Date'] = "Not available"
    #                     tmp['Likes'] = "Not available"
    #                     tmp['Disclike'] = "Not available"
    #                     tmp['Url'] = video_url
    #                     tmp['Poster-Image_uri'] = block.find_element(By.CLASS_NAME, "video_screenshot").get_attribute('src')
    #                     tmp['Category'] = website_name
    #                     tmp['video_download_url'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
    #                     tmp['poster_download_uri'] = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
    #                     tmp['Video-name'] = f'{video_name}.mp4'
    #                     tmp['Photo-name'] = f'{video_name}.jpg'
    #                     tmp['Pornstarts'] = "Not available"
    #                     tmp['Username'] = self.revsharecash.website_name

    #                     response = requests.get(tmp['Poster-Image_uri'])
    #                 image_file_path = os.path.join(collection_path, f'{video_name}.jpg')
    #                 with open(image_file_path, 'wb') as file:
    #                     file.write(response.content)
    #                 image_file_path = self.copy_files_in_media_folder(image_file_path)
                        

    #                 url = self.driver.find_elements(By.XPATH, '//a[contains(@href, "fhd.mp4")]')[1].get_attribute('href')
    #                 video_file_path = os.path.join(collection_path, tmp['Video-name'])
    #                 self.download_video_from_request(url,video_file_path)
    #                 video_file_path = self.copy_files_in_media_folder(video_file_path)
                    
    #                 cetegory_obj, _ = cetegory.objects.get_or_create(category = "defloration")
    #                 videos_data_obj = VideosData.objects.create(
    #                         video = video_file_path,
    #                         image = image_file_path,
    #                         Username = self.revsharecash.username,
    #                         Likes = 0,
    #                         Disclike = 0,
    #                         Url = self.driver.current_url,
    #                         Title = tmp["Title"],
    #                         Discription = tmp["Discription"],
    #                         Release_Date = tmp["Release-Date"],
    #                         Poster_Image_url = tmp["Poster-Image_uri"],
    #                         Video_name = tmp["Video-name"],
    #                         Photo_name = tmp["Photo-name"],
    #                         Pornstarts = tmp["Pornstarts"],
    #                         configuration = self.revsharecash,
    #                         cetegory = cetegory_obj
    #                     )
    #                 found_videos += 1

    #             if not found_videos >= max_video:
    #                 # pagignation
    #                 self.driver.get(website_url)
    #                 self.click_element('next btn', 'arrow_next', By.CLASS_NAME)
    #                 website_url = self.driver.current_url
    #     # except Exception as e:
    #     #     print(e)