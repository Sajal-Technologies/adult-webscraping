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