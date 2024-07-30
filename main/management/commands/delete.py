from django.core.management.base import BaseCommand, CommandError
from pytz import timezone, utc
from main.models import configuration as conf
from scrapping.settings import BASE_DIR
import os
from collections import defaultdict
import pandas as pd
from datetime import datetime, timedelta, tzinfo, timezone
from main.models import videos_collection

all_Videos = []
bas_csv_path = '/home/sajal/adult-webscraping/csv'
files = os.listdir('/home/sajal/adult-webscraping/csv')

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
        self.all_not_need_dele_videos = []
        self.main_video_li = []

        self.create_dict_videos_from_csv()
        self.create_dict_videos_from_db()

        def get_videos_to_delete(keep_videos, all_videos):
            all_video_names = [os.path.basename(video) for video in all_videos]
            videos_to_delete = [video for video, name in zip(all_videos, all_video_names) if name not in keep_videos]
            return videos_to_delete

        self.main_video_li = get_videos_to_delete(self.all_not_need_dele_videos, all_Videos)

        for m_video in self.main_video_li:
            self.check_video_exists(m_video)

    def check_video_exists(self, file_path):
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"File '{file_path}' has been deleted.")
            except Exception as e:
                print(f"Error occurred while deleting file '{file_path}': {e}")
        else:
            print(f"File '{file_path}' does not exist.")

    def is_more_than_last_two_days_string(self, date_string, days):
        given_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
        current_date = datetime.now()
        time_difference = current_date - given_date

        if time_difference >= timedelta(days=days):
            return True
        else:
            return False

    def is_more_than_last_two_days_datetime(self, given_date, days):

        current_date = datetime.now(timezone.utc)
        time_difference = current_date - given_date

        if time_difference >= timedelta(days=days):
            return True
        else:
            return False

    def delete_videos(self):

        for key, list_ in self.data.items():
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
                    if not self.is_more_than_last_two_days_string(vd_downloaded_time, 2):
                        self.data[file_path].append(vd_name)
                        self.all_not_need_dele_videos.append(vd_name)
                        df = df.drop(idx)
                        df.to_csv(file_path)


    def create_dict_videos_from_db(self):
        all_videos_collection = videos_collection.objects.all()
        for vid in all_videos_collection:
            if not self.is_more_than_last_two_days_datetime(vid.created, 2):
                self.all_not_need_dele_videos.append(vid.Video_name)
            else:
                vid.delete()
