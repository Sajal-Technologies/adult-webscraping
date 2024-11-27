from driver.get_driver import StartDriver
import json, random, os, time, requests, urllib, shutil, re
from utils.mail import SendAnEmail
from bs4 import BeautifulSoup
from app.models import cetegory, configuration, videos_collection, VideosData
from dateutil import parser
from datetime import datetime, timedelta
import pandas as pd
from urllib.parse import unquote

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
from anticaptchaofficial.recaptchav2proxyless import *



class Bot(StartDriver):
    def solve_2captcha(self,site_key, site_url):
        solver = TwoCaptcha('6e00098870d05c550b921b362c2abde8')
        response = solver.turnstile(sitekey=site_key,url=site_url,                             action='challenge',                            useragent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
        # captcha_url = "http://2captcha.com/in.php"
        # api_key = '6e00098870d05c550b921b362c2abde8'
        # captcha_payload = {'key': api_key, 'method': 'turnstile', 'googlekey': site_key, 'pageurl': site_url, "json": 1 }
        # response = requests.post(captcha_url, data=captcha_payload)
        if response:
            captcha = response['code']
            return captcha
        else:
            raise Exception("Error submitting CAPTCHA: " + response.text)
        
    def vip4k_login(self):
        # self.CloseDriver()
        # self.driver = Driver(uc=True, headless=headless)
        for i in range(3):
            self.driver.get('https://www.nowsecure.nl')
            self.driver.get('https://vip4k.com/en/login')
            login = self.find_element('login button','//*[text()="Login"]')
            if login:
                self.load_cookies(self.vip4k.website_name)
                login = self.find_element('login button','//*[text()="Login"]')
                if login:
                    self.click_element('login button','//*[text()="Login"]')
                    self.random_sleep(2,4)
                    self.input_text(self.vip4k.username,'username','login-username',By.ID)
                    self.random_sleep(2,3)
                    self.input_text(self.vip4k.password,'password','login-password',By.ID)
                    self.random_sleep(2,3)
                    site_key_ele = self.find_element('SITE-KEY','g-recaptcha',By.CLASS_NAME)
                    if site_key_ele:
                        solver = recaptchaV2Proxyless()
                        solver.set_verbose(1)
                        solver.set_key("e49c2cc94651faab912d635baec6741f")    
                    #     # to solvee the captcha
                        site_key = site_key_ele.get_attribute('data-sitekey')
                        g_response = self.solve_2captcha(site_key=site_key, site_url=self.driver.current_url)
                        self.driver.execute_script(f'''var els=document.getElementsByName("g-recaptcha-response");for (var i=0;i<els.length;i++) {{els[i].value = "{g_response}";}}''')

                    #     solver.set_website_url(self.driver.current_url)
                    #     solver.set_website_key(site_key)
                    #     solver.set_soft_id(0)
                    #     g_response = solver.solve_and_return_solution()
                        
                    #     if g_response == 0:
                    #         print ("task finished of captcha solver with error "+solver.error_code)
                    #         return False
                    #     print ("g-response: "+g_response)
                        # self.driver.execute_script(f'document.querySelector("#cf-chl-widget-65aqx_g_response").value="{g_response}";')
                        # self.driver.execute_script(f'document.querySelector("#cf-chl-widget-ixf9o_g_response").value="{g_response}";')
                        # aa  = self.find_element('response', 'g-recaptcha-response', By.NAME)
                        # self.driver.execute_script(f'document.getElementsByName("g-recaptcha-response").value = "{g_response}";')
                    # iframe = WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, f'//iframe[@title="reCAPTCHA"]')))
                    # self.driver.execute_script('document.querySelector("#recaptcha-token").click()')
                    # self.driver.switch_to.default_content()
                    # self.random_sleep(2,3)
                    # iframe = WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, f'//iframe[@title="recaptcha challenge expires in two minutes"]')))        
                    # self.click_element('click extension btn','//*[@id="rc-imageselect"]/div[3]/div[2]/div[1]/div[1]/div[4]')
                    
                    # self.driver.switch_to.default_content()
                    
                    # self.random_sleep(10,15)
                    self.click_element('submit','//input[@type="submit"]')
                    self.random_sleep(5,6)
            if self.find_element('check login','//div[@class="logout__text"]'):
                cookies = self.get_cookies(self.vip4k.website_name)
                # member_cookies = [item for item in cookies if item.get("domain") != ".vip4k.com"]
                # for item in member_cookies:self.driver.add_cookie(item)
                # self.driver.quit()
                # self.get_driver()
                # self.driver.get('https://vip4k.com/en/login')
                # self.load_cookies(self.vip4k.website_name)
                return True
            
    def download_all_vip_channels_video(self):
        self.driver.get('https://members.vip4k.com/en/channels')
        all_li = self.driver.find_elements(By.XPATH, '//li[@class="grid__item"]')
        if all_li:
            all_channel_url = [li.find_element(By.TAG_NAME, 'a').get_attribute('href') for li in all_li]
            for channel in all_channel_url:
                video_dict = self.vip4k_get_video(channel, True)
                self.vip4k_download_video(video_dict)

        
    def vip4k_get_video(self,url :str='', channel: bool= False):
        
        video_detailes = {'collection_name':'','video_list':[]}
        videos_urls = []
        if channel: self.driver.get(url)
        else:self.driver.get(f'https://members.vip4k.com/en/tag/{self.vip4k.category}')
        self.random_sleep(10,15)
        collection_name = self.find_element('collection name','//h1[@class="section__title title title--sm"]', timeout=5)
        if not collection_name: collection_name = self.find_element('collection name','//h1')
        video_detailes['collection_name'] = collection_name.text.lower().replace(' ','_')
        new_csv= True if '4k' in video_detailes['collection_name'] or 'sis_videos' in video_detailes['collection_name'] else False
        website_name = f"vip4k_{video_detailes['collection_name']}" if new_csv else self.vip4k.website_name
        self.make_csv(website_name, new=new_csv)
        # if new_csv:
        df_url = self.column_to_list(self.vip4k.website_name,'Url')
        max_video = self.vip4k.numbers_of_download_videos
        while len(videos_urls) < max_video:
            ul_tag = self.find_element('ul tag', 'grid.sets_grid', By.CLASS_NAME)
            li_tags = ul_tag.find_elements(By.TAG_NAME, 'li')
            for li in li_tags:
                video_date = li.find_element(By.CLASS_NAME, 'item__date').text
                if video_date and self.date_older_or_not(video_date):
                    video_url = li.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    post_url = li.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    if video_url and not post_url: 
                        self.random_sleep(5,7)
                        post_url = li.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    if video_url and post_url:
                        if video_url not in df_url and video_url not in [item['video_url'] for item in videos_urls]:
                            videos_urls.append({"video_url": video_url, 'post_url': post_url})
                            if len(videos_urls) >= max_video:break
                    if len(videos_urls) >= max_video:break
            if len(videos_urls) >= max_video:break
            show_more = self.find_element('show more','/html/body/div[2]/div/div[1]/div/section/div[5]/a')
            if show_more:
                self.driver.execute_script("arguments[0].scrollIntoView();", show_more)
                show_more.click()
            else:
                break
        video_detailes['video_list'] = videos_urls
        return video_detailes
    
    def vip4k_download_video(self,videos_dict : dict):
        self.driver.save_screenshot('driver.png')
        videos_urls = videos_dict['video_list']
        collection_name = videos_dict['collection_name']
        collection_path = self.create_or_check_path(self.vip4k_category_path,sub_folder_=collection_name)
        new_csv= True if '4k' in collection_name or 'sis_videos' in collection_name else False
        website_name = f'vip4k_{collection_name}' if new_csv else self.vip4k.website_name

        for idx, video_url in enumerate(videos_urls):
            self.driver.get(video_url['video_url'])
            # self.find_element()
            self.random_sleep(10,15)
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
                    "Username" : self.vip4k.website_name,
                }
            try:
                likes_count = self.find_element('Likes count','//button[@class="player-vote__item player-vote__item--up "]')
                if likes_count :
                    tmp['Likes'] = likes_count.text

                # self.getvalue_byscript('document.querySelector("#root > div.sc-yo7o1v-0.hlvViO > div.sc-yo7o1v-0.hlvViO > div.sc-1fep8qc-0.ekNhDD > div.sc-1deoyo3-0.iejyDN > div:nth-child(1) > div > section > div.sc-1wa37oa-0.irrdH > div.sc-bfcq3s-0.ePiyNl > div.sc-k44n71-0.gbGmcO > span:nth-child(1) > strong").textContent')
                Disclike_count = self.find_element('Disclike count','//button[@class="player-vote__item player-vote__item--down "]')
                if Disclike_count :
                    tmp['Disclike'] = Disclike_count.text

                Title = self.find_element('Title','//h1[@class="player-description__title"]')
                if Title :
                    tmp['Title'] = Title.text

                Release = self.find_element('Release',"//li[@class='player-additional__item'][2]")
                if Release :
                    tmp['Release-Date'] = Release.text

                Discription = self.find_element('Discription','//div[@class="player-description__text"]')
                if Discription :
                    tmp['Discription'] = Discription.text

                porn_starts = self.driver.find_elements(By.XPATH,'//div[@class="model__name"]')
                if porn_starts:
                    porn_start_name = ''
                    for i in porn_starts:
                        porn_start_name += f'{i.text},'
                    tmp['Pornstarts'] = porn_start_name.rstrip(',')
                video_name = f"vip4k_{collection_name.replace('_videos', '')}_{self.sanitize_title(tmp['Title'])}"

                v_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.mp4'.replace('\\', '/')
                p_url = f'http://208.122.217.49:8000{collection_path.replace(self.base_path,"")}/{video_name}.jpg'.replace('\\', '/')
                tmp['poster_download_uri'] = p_url
                tmp['video_download_url'] = v_url
                tmp['Photo-name'] = f'{video_name}.jpg'
                tmp['Video-name'] = f'{video_name}.mp4'
                response = requests.get(video_url['post_url'])
                with open(f'{collection_path}/{video_name}.jpg', 'wb') as f:f.write(response.content)
                local_filename =  os.path.join(collection_path, f'{video_name}.mp4')
                FullHD_link = self.driver.find_element(By.XPATH, '//a[contains(@download, "FullHD.mp4")]').get_attribute('data-download')
                if FullHD_link:
                    self.driver.get(f'https://members.vip4k.com{FullHD_link}')
                    self.random_sleep(2,3)
                    page_source = self.driver.page_source
                    start = page_source.find('<pre>') + 5
                    end = page_source.find('</pre>', start)
                    json_data = page_source[start:end]
                    data = json.loads(json_data)
                    decoded_url = unquote(data['url']).replace('\\/', '/')
                    self.download_video_from_request(decoded_url, local_filename)
                else:continue

                # js_script = """
                #     var downloadLinks = document.querySelectorAll('.download__item');
                #     for (var i = 0; i < downloadLinks.length; i++) {
                #         var link = downloadLinks[i];
                #         if (link.getAttribute('download').includes('FullHD.mp4')) {
                #             link.click();
                #             break;
                #         }
                #     }
                #     """
                # self.driver.execute_script(js_script)
                # file_name = self.wait_for_file_download(timeout=30)
                # if not file_name: 
                #     print('file downloading not started')
                #     continue
                # self.random_sleep(3,5)
                # name_of_file = os.path.join(self.download_path, f'{video_name}.mp4')
                # os.rename(os.path.join(self.download_path,file_name), name_of_file)
                # self.copy_files_in_catagory_folder(name_of_file,collection_path)
                self.set_data_of_csv(website_name,tmp,video_name)
            except Exception as e:
                print('Error:', e)