import os
import asyncio
import pathlib
import nodriver as uc
from nodriver.core.browser import CookieJar
from bs4 import BeautifulSoup


class vip4k:
    
    def __init__(self) -> None:
        self.base_path = os.getcwd()
        self.download_path = os.path.join(self.base_path, 'downloads')

    async def get_driver(self):
        browser = await uc.start()
        await browser.get('https://www.nowsecure.nl')
        await asyncio.sleep(5)  # Use asyncio.sleep instead of time.sleep  
        self.page  = await browser.get('https://vip4k.com/en/login')
        await self.page.set_download_path(pathlib.Path(self.download_path))
        await self.page.add_handler()

    async def login(self):
        await asyncio.sleep(30)  # Use asyncio.sleep instead of time.sleep  
        username = await self.page.select('[id="login-username"]')
        await username.send_keys('efc_4kporn_2')  # Add await here
        password = await self.page.select('[id="login-password"]')
        await password.send_keys('84w5gb845gv')  # Add await here
        login_btn = await self.page.select('[value="Login"]')
        await login_btn.click()  # Add await here
        # logout_btn = await self.page.find('Logout', best_match=True)
        # if logout_btn:
        #     return True
        # return False

    async def download_all_vip_channels_video(self):
        await self.page.get('https://members.vip4k.com/en/channels')
        await asyncio.sleep(20)  # Use asyncio.sleep instead of time.sleep  
        all_li  = await self.page.query_selector_all('a[href]')
        all_link = []
        all_channel = ["black4k", "bride4k", "cuck4k", "daddy4k","debt4k", "dyke4k", "fist4k", "loan4k", "mature4k", "old4k", "pie4k", "rim4k", "shame4k", "sis","stuck4k", "tutor4k", "vip4k"]
        for link in all_li:
            soup = BeautifulSoup(str(link), 'html.parser')
            # Find the <a> tag
            a_tag = soup.find('a')
            # Extract the href attribute value
            href_value = a_tag.get('href')
            print("href_value:-->",href_value)
            if '/en/channels/' in href_value and any(channel in href_value for channel in all_channel):
                all_link.append(href_value)
        

    async def work(self):
        await self.get_driver()
        await self.login()
        await self.download_all_vip_channels_video()
        ...

if __name__ == '__main__':
    bot = vip4k()
    uc.loop().run_until_complete(bot.work())
