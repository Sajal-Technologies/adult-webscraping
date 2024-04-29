from undetected_chromedriver import Chrome, ChromeOptions
import os

base_path = os.getcwd()


def opt():
    options = ChromeOptions()
    options.add_argument('--lang=en')  
    # options.add_argument('log-level=3')  
    options.add_argument('--mute-audio') 
    options.add_argument("--enable-webgl-draft-extensions")
    options.add_argument('--mute-audio')
    options.add_argument("--ignore-gpu-blocklist")
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--headless')

    prefs = {"credentials_enable_service": True,
            'profile.default_content_setting_values.automatic_downloads': 1,
            "download.default_directory" : f"downloads",
        'download.prompt_for_download': False, 
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True ,
        "profile.password_manager_enabled": True}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')    
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--enable-javascript")
    options.add_argument("--enable-popup-blocking")
    options.add_extension(os.path.join(base_path,'Stay-secure-with-CyberGhost-VPN-Free-Proxy.crx'))
    options.add_extension(os.path.join(base_path,'Buster-Captcha-Solver-for-Humans.crx'))
    return options

def open_vps_driver():
    """Start webdriver and return state of it."""
    options = opt()
    driver = Chrome(options=options)
    return driver
    


import time
import random, json
from typing import Union
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException


class WebDriverUtility:
    def __init__(self) -> None:
        pass

    def get_driver(self):
        pass

    def close_driver(self):
        self.driver.quit()

    def navigate_to(self, url):
        self.driver.get(url)

    def safe_send_keys(self, locator, text, by=By.XPATH, timeout=10):
        element = self.find_element(locator, by, timeout)
        if element:
            element.send_keys(text)

    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def wait_for_element_visible(self, locator, by=By.XPATH, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, locator))
            )
        except TimeoutException:
            print(f"Element with locator {locator} not visible within {timeout} seconds")
            return None

    def wait_for_element_invisible(self, locator, by=By.XPATH, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((by, locator))
            )
        except TimeoutException:
            print(f"Element with locator {locator} still visible after {timeout} seconds")
            return False

    def get_text(self, locator, by=By.XPATH, default=""):
        element = self.find_element(locator, by)
        return element.text if element else default

    def find_element(self, locator, by=By.XPATH, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            return element
        except TimeoutException:
            print(f"Timeout while trying to find element with locator: {locator}")
            return None
    
    def find_elements(self, locator, by=By.XPATH, timeout=10):
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, locator))
            )
            return elements
        except TimeoutException:
            print(f"Timeout while trying to find elements with locator: {locator}")
            return []

    def click_element(self, locator, by=By.XPATH, timeout=10):
        element = self.find_element(locator, by, timeout)
        if element:
            self.ensure_click(element)

    def ensure_click(self, element, attempts=3):
        successful = False
        current_attempt = 0
        while not successful and current_attempt < attempts:
            try:
                element.click()
                successful = True
            except ElementClickInterceptedException:
                print("Element is not clickable, attempting to scroll and retry.")
                self.scroll_to_element(element)
            except StaleElementReferenceException:
                print("Stale element reference, re-fetching the element.")
                element = self.refresh_element(element)
            except Exception as e:
                print(f"Unexpected error clicking element: {str(e)}")
            finally:
                current_attempt += 1

        if not successful:
            print("Attempting final click using JavaScript.")
            self.click_with_javascript(element)

    def refresh_element(self, element):
        # Re-find the element in the DOM to avoid StaleElementReferenceException
        locator = element.get_attribute('xpath')
        return self.find_element(locator)

    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def click_with_javascript(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def capture_screenshot(self, file_path):
        self.driver.save_screenshot(file_path)

    def get_all_tabs(self):
        return self.driver.window_handles
    
    def switch_to_tab(self, window_name:str):
        self.driver.switch_to.window(window_name)

    def switch_to_iframe(self, frame_reference: Union[str, int, WebElement]):
        self.driver.switch_to.frame(frame_reference)
    
    def getvalue_byscript(self,script = ''):
        value = self.driver.execute_script(f'return {script}')  
        return value
    
    def new_tab(self, url=None):
        self.driver.tab_new(url)
    
    def random_sleep(self,a=3,b=7,reson = ""):
        random_time = random.randint(a,b)
        print('time sleep randomly :',random_time) if not reson else print('time sleep randomly :',random_time,f' for {reson}')
        time.sleep(random_time)

    def scroll_smoothly(self, direction="down", max_scroll=3):
        """ Scroll smoothly in the specified direction.
        
        :param direction: 'up' or 'down'
        :param max_scroll: maximum number of scroll actions
        """
        scroll_count = 0
        while scroll_count < max_scroll:
            if direction == "down":
                self.driver.execute_script("window.scrollBy(0, window.innerHeight/4);")
            else:
                self.driver.execute_script("window.scrollBy(0, -window.innerHeight/4);")
            time.sleep(random.uniform(0.5, 1.5))  # Random sleep to mimic human behavior
            scroll_count += 1

    def load_cookies(self, load_path):
        """ Load cookies from a file and add them to the current session. """
        with open(load_path, 'r') as file:
            cookies = json.load(file)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
    
    def get_cookies(self, save_path):
        """ Save all cookies to a file. """
        cookies = self.driver.get_cookies()
        with open(save_path, 'w') as file:
            json.dump(cookies, file)

    def refresh_driver(self):
        self.driver.refresh()







def get_brazzers_videos_url(self, url=None,collection=None, tag=None):
    video_details = {'collection_name': '', 'video_list': []}
    videos_urls = []
    if collection:
        self.driver.get(f'https://site-ma.brazzers.com/scenes?{tag}')
    elif url:
        self.driver.get(url)
    else:
        self.brazzers_get_categories()
    found_max_videos = self.brazzers.numbers_of_download_videos
    self.random_sleep(6, 10)

    collection_name = f'brazzers_{collection}_videos'.replace('brazzers_brazzers_', 'brazzers')
    video_details['collection_name'] = collection_name
    self.make_csv(collection_name, new=True) if collection else None

    df_url = self.column_to_list(collection_name, 'Url')
    
    while len(videos_urls) < found_max_videos:
        all_thumbs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'one-list-1vyt92m')]")
        for thumb in all_thumbs:
            try:
                video_date = thumb.find_element(By.XPATH, ".//div/div[2]/div/div[2]")
                if self.date_older_or_not(video_date.text):
                    video_url = thumb.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    post_url = thumb.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    if video_url not in df_url:
                        videos_urls.append({"video_url": video_url, 'post_url': post_url})
                        if len(videos_urls) >= found_max_videos:
                            break
            except Exception as e:
                print(e)
        
        if len(videos_urls) < found_max_videos:
            next_page_link = self.find_element('ul', "ul.eqrwdcp0.one-list-fhj8o6.e13hbd3c0", By.CSS_SELECTOR).find_elements(By.TAG_NAME, 'li')[-2]
            if next_page_link:
                self.ensure_click(next_page_link)
            else:
                break

    video_details['video_list'] = videos_urls
    return video_details