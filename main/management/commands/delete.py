from django.core.management.base import BaseCommand, CommandError
from main.models import configuration as conf
from scrapping.settings import BASE_DIR
import os
from collections import defaultdict
import pandas as pd
from datetime import datetime, timedelta
from main.models import videos_collection

all_Videos = []
bas_csv_path = '/home/rk/workspace/Sajal/adult-webscraping/csv'
files = os.listdir('/home/rk/workspace/Sajal/adult-webscraping/csv')

base_name_dict = defaultdict(list)
for file in files:
    base_name = file.split('_')[0]
    base_name_dict[base_name].append(file)

for foldername, subfolders, filenames in os.walk(os.path.join(os.getcwd(), 'downloads')):
    all_Videos.append(os.path.join(foldername, filenames[0]) if len(filenames) > 0 else None)

all_Videos = [i for i in all_Videos if i]
all_Videos_name_dict = {}
for i in all_Videos:
    Videos_name = i.split('/')[-1]
    if Videos_name.endswith('.jpg'): continue
    all_Videos_name_dict[Videos_name] = i

class Command(BaseCommand):
    help = "Closes the specified poll for voting"


    def handle(self, *args, **options):
        self.data = {}
        self.all_need_dele_videos = []

        self.create_dict_videos_from_csv()
        self.create_dict_videos_from_db()


    def is_within_last_two_days(self,date_string, days):
        # Parse the datetime string
        given_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')

        # Get the current date and time
        current_date = datetime.now()

        # Calculate the time difference
        time_difference = current_date - given_date

        # Check if the time difference is less than 2 days
        if time_difference <= timedelta(days=days):
            return True
        else:
            return False
    def create_dict_videos_from_csv(self):

        for file in files:
            file_path = os.path.join(bas_csv_path, file)
            df = pd.read_csv(file_path)
            if df.empty: continue

            if 'Video-title' in df.columns:

                if not file_path in self.data.keys():
                    self.data[file_path] = []

                for idx, row in df.iterrows():
                    vd_name = row['Video-title']
                    vd_downloaded_time = row['downloaded_time']

                    if not self.is_within_last_two_days(vd_downloaded_time, 2):
                        self.data[file_path].append(vd_name)
                        self.all_need_dele_videos.append(vd_name)
                        df = df.drop(idx)
                        # df.to_csv(file_path)   # later need to uncomment

    def create_dict_videos_from_db(self):
        videos_collection.objects.all()
        breakpoint()
