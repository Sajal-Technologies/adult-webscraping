from driver.get_driver import StartDriver
import json, random, os, time, requests, shutil
from utils.mail import SendAnEmail
from app.models import cetegory, configuration, videos_collection, VideosData
from datetime import datetime, timedelta
from dateutil import parser

# selenium imports
from selenium.common.exceptions import NoSuchElementException, TimeoutException,ElementNotInteractableException,NoSuchElementException,WebDriverException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver


# django
from Scrape.settings import MEDIA_URL


class Bot(StartDriver):
    
  
    
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
        self.load_cookies(self.brazzers.website_name)
        self.driver.get('https://site-ma.brazzers.com/store')
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
                    if self.find_element("agreement","//div[contains(text(), 'Existing users access')]",timeout=5):
                        self.click_element("Sign in","/html/body/div/main/div/section/a")
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
        
        for i in self.driver.find_elements(By.TAG_NAME,'a') : 
            if "https://site-ma.brazzers.com/scenes?tags" in i.get_attribute('href') :
                if i.text.lower() == self.brazzers.main_category.lower() :
                    i.click()
                    return True
        
        for i1 in range(1,6) :
            cate1 = self.find_element('category',f'//*[@id="root"]/div[1]/div[2]/div[3]/div[2]/div[2]/div[{i1}]/div/div/a',timeout= 1)
            if cate1 : 
                if cate1.text.lower() == self.brazzers.main_category.lower() :
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
                            if cate1.text.lower() == self.brazzers.main_category.lower() :
                                found_category = True
                                self.click_element('category', f'//*[@id="root"]/div[1]/div[2]/div[3]/div[2]/div[{i2}]/div[{i3}]/div/div/a',timeout=1)
                                break
                else : break
                if found_category == True : break
        
        if found_category == True : 
            return True
        else: 
            return False
    
    def get_brazzers_videos_url(self,url=None, collection=None, tag=None):
        video_detailes = {'collection_name':'','video_list':[]}
        videos_urls = []
        if collection:
            self.driver.get(f'https://site-ma.brazzers.com/scenes?{tag}')
        elif url:
            self.driver.get(url)
        else:
            if not self.driver.current_url.lower() == self.brazzers_category_url : 
                self.driver.get(self.brazzers_category_url)
                self.random_sleep(7,10)

            for i in self.driver.find_elements(By.TAG_NAME,'a') : 
                print(i.text)
                if "https://site-ma.brazzers.com/scenes?tags" in i.get_attribute('href') :
                    
                    if i.text.lower() == self.brazzers.main_category.lower() :
                        i.click()
                        break
            else :
                return video_detailes

        found_max_videos = self.brazzers.numbers_of_download_videos
        self.random_sleep(6,10)
        
        video_detailes['collection_name'] = "Brazzers_category_videos"   
        
        self.check_csv_exist(self.csv_name)
        df_url = [i.Url for i in VideosData.objects.filter(configuration=self.brazzers)]

        while len(videos_urls) <= found_max_videos: 
            self.random_sleep(10,15)
            all_thumb = self.driver.find_elements(By.XPATH,"//div[contains(@class, 'one-list-1vyt92m') and contains(@class, 'e1vusg2z1')]" )
            try :
                for thumb in all_thumb: 
                    video_date = thumb.find_element(By.XPATH, ".//div/div[2]/div/div[2]")
                    self.driver.execute_script("arguments[0].scrollIntoView();", video_date)
                    time.sleep(0.3)
                    if video_date :
                        today = datetime.now()
                        old_date = today - timedelta(days=self.brazzers.more_than_old_days_download)
                        date_obj = parser.parse(video_date.text)
                        if date_obj < old_date :
                            video_url = thumb.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            post_url = thumb.find_element(By.TAG_NAME, 'img').get_attribute('src')
                            if video_url and post_url and video_url not in df_url:
                                print(f'add video url in lists')
                                videos_urls.append({"video_url":video_url,'post_url':post_url})
                                if len(videos_urls) >= found_max_videos:
                                    break
            except Exception as e :
                print(e)

            if len(videos_urls) >= found_max_videos :
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
            self.random_sleep(20,25)
            video_name = f"{collection_name}_{self.sanitize_title(self.driver.current_url.split('https://site-ma.brazzers.com/')[-1])}"
            v_url = f'http://208.122.217.49:8000/API/downloads/Brazzers_category_videos/{video_name}.mp4'.replace('\\', '/')
            p_url = f'http://208.122.217.49:8000/API/downloads/Brazzers_category_videos/{video_name}.jpg'.replace('\\', '/')
            tmp = {
                    "Likes" : 0,
                    "Disclike" :0,
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
                else:
                    tmp['Likes'] = 0
                    

                # self.getvalue_byscript('document.querySelector("#root > div.sc-yo7o1v-0.hlvViO > div.sc-yo7o1v-0.hlvViO > div.sc-1fep8qc-0.ekNhDD > div.sc-1deoyo3-0.iejyDN > div:nth-child(1) > div > section > div.sc-1wa37oa-0.irrdH > div.sc-bfcq3s-0.ePiyNl > div.sc-k44n71-0.gbGmcO > span:nth-child(1) > strong").textContent')
                Disclike_count = self.find_element('Disclike count','//*[text()="Dislikes:"]/strong')
                if Disclike_count :
                    tmp['Disclike'] = Disclike_count.text
                else:
                    tmp['Disclike'] = 0

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
                port_starts = self.find_element('pornstars','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[5]/div/section/div/div/div/h2')
                if port_starts :
                    tmp['Pornstarts'] = port_starts.text
                else :
                    port_starts = self.find_element('pornstars','/html/body/div/div[1]/div[2]/div[3]/div[2]/div[5]/div/section/div/div/div/h2')
                    if port_starts :
                        tmp['Pornstarts'] = port_starts.text
                    
                
                response = requests.get(video_url['post_url'])
                with open(f'{collection_path}/{video_name}.jpg', 'wb') as f:f.write(response.content)
                self.click_element('download btn', '//button[@class="sc-yox8zw-1 VZGJD sc-rco9ie-0 jnUyEX"]') 
                self.click_element('download high_quality','//div[@class="sc-yox8zw-0 cQnfGv"]/ul/div/button[1]')
                file_name = self.wait_for_file_download()
                self.random_sleep(3,5)
                name_of_file = os.path.join(self.download_path,"Brazzers_category_videos", f'{video_name}.mp4')
                os.rename(os.path.join(self.download_path,file_name), name_of_file)
                self.random_sleep(3,5)
                
                
                os.makedirs(os.path.join(os.getcwd(),'media','videos',"Brazzers_category_videos"),exist_ok=True)
                if os.path.exists(name_of_file) :
                    video_file = self.copy_files_in_media_folder(name_of_file)
                    
                os.makedirs(os.path.join(os.getcwd(),'media','image',"Brazzers_category_videos"),exist_ok=True)
                image_file = f'{collection_path}/{video_name}.jpg'
                if os.path.exists(image_file) :
                    image_file = self.copy_files_in_media_folder(image_file,folder="img")
                    image_file = f"/image/Brazzers_category_videos/{video_name}.jpg"
                    
                videos_data_obj = VideosData.objects.create(
                    video = video_file,
                    image = image_file,
                    Username = self.brazzers.username,
                    Likes = tmp['Likes'],
                    Disclike = tmp['Disclike'],
                    Url = self.driver.current_url,
                    Title = tmp['Title'],
                    Discription = tmp['Discription'],
                    Release_Date = tmp["Release-Date"],
                    Poster_Image_url = tmp["Poster-Image_uri"],
                    Video_name = tmp["Video-name"],
                    Photo_name = tmp["Photo-name"],
                    Pornstarts = tmp["Pornstarts"],
                    configuration = self.brazzers
                )
                if not Site_name :
                    cetegory_obj, _ = cetegory.objects.get_or_create(category = self.brazzers.main_category)
                    if cetegory_obj not in self.brazzers.category.all():
                        # Add the category to the configuration's category list
                        self.brazzers.category.add(cetegory_obj)
                    videos_data_obj.cetegory = cetegory_obj
                    videos_data_obj.save()
                else:
                    cetegory_obj, _ = cetegory.objects.get_or_create(category = Site_name)
                    if cetegory_obj not in self.brazzers.category.all():
                        # Add the category to the configuration's category list
                        self.brazzers.category.add(cetegory_obj)
                    videos_data_obj.cetegory = cetegory_obj
                    videos_data_obj.save()
            except Exception as e:
                print('Error:', e)