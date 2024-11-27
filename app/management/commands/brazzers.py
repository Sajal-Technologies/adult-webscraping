from django.core.management.base import BaseCommand, CommandError
from Scrape.settings import BASE_DIR
from django.core.files.base import ContentFile
from app.models import videos_collection, configuration, VideosData
import requests, os, time
from driver.Bots.brazzers import Bot
from utils.mail import SendAnEmail

class Command(BaseCommand, Bot):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("--only_login", default=False, type=bool)
    
    def download_and_save_file(self,url):
        # Fetch the file from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Extract the filename from the URL (optional)
        filename = url.split('/')[-1]

        video_instance = videos_collection.objects.create(Title="title")
        video_instance.video.save(filename, ContentFile(response.content), save=True)

    def make_init(self):
        
        self.brazzers_category_url = 'https://site-ma.brazzers.com/categories'
        self.driver_type = "normal"     
        self.base_path = os.getcwd()
        
        self.download_path = os.path.join(os.getcwd(),'downloads')
        [ os.remove(os.path.join(os.getcwd(),'downloads',i)) for i in os.listdir('downloads') if i.endswith('.crdownload') or i.endswith('.mp4') ]
        
        self.brazzers = configuration.objects.get(website_name='brazzers')
        self.brazzers_category_path = self.create_or_check_path('Brazzers_category_videos')
        
        self.csv_folder_path = self.create_or_check_path('csv',main=True)
        self.cookies_path = self.create_or_check_path('cookies',main=True)
        self.csv_name = "Brazzers.csv"
        self.csv_path = os.path.join(self.csv_folder_path,f'{self.csv_name}')

    def handle(self, *args, **options):
        VideosData.delete_older_videos()
        
        self.make_init()
        self.driver = self.get_driver()
        if not self.driver :
            SendAnEmail('Could not open up the driver')
            return
        
        only_login = options["only_login"]
        if only_login :
            print('only login')
            if self.brazzers_login():
                self.brazzers.lastime_able_to_login_or_not = True
                self.brazzers.save()
            else:
                self.brazzers.lastime_able_to_login_or_not = False
                self.brazzers.save()
        else :
            print('Not only login')
            
        if self.brazzers_login():
            self.brazzers.lastime_able_to_login_or_not = True
            self.brazzers.save()
            video_dict = self.get_brazzers_videos_url()
            self.download_brazzer_videos(video_dict)
            tags_102 = self.get_brazzers_videos_url(url='https://site-ma.brazzers.com/scenes?addon=102')
            self.download_brazzer_videos(tags_102, 'addon_102')  # mofos
            tags_152 = self.get_brazzers_videos_url(url='https://site-ma.brazzers.com/scenes?addon=152')
            self.download_brazzer_videos(tags_152, 'addon_152')  # reality kings
            tags_162 = self.get_brazzers_videos_url(url='https://site-ma.brazzers.com/scenes?addon=162')
            self.download_brazzer_videos(tags_162, 'addon_162')  # brazzers_main
        else:
            self.brazzers.lastime_able_to_login_or_not = False
            self.brazzers.save()
    
    
    
        # self.download_and_save_file("http://208.122.217.49:8000/csv/vip4k_debt4k_videos_details.csv")