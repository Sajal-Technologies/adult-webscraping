from django.core.management.base import BaseCommand, CommandError
from main.models import configuration as conf
from scrapping.settings import BASE_DIR
from mail import SendAnEmail

class Command(BaseCommand):
    help = "Closes the specified poll for voting"


    def handle(self, *args, **options): 
        from bot import scrapping_bot
        from utils import close_every_chrome
        logggg = False
        for _ in range(1):
            try:
                bot = scrapping_bot(brazzers_bot=False)
                driver = bot.starting_bots()
                if not driver:
                    SendAnEmail('Could not open up the driver')
                    return
                print('Vip 4k process')
                if bot.vip4k_login():
                    logggg = True
                    # all_channel = ["Black4k", "Bride4k", "Cuck4k", "Daddy4k","Debt4k", "Dyke4k", "Fist4k", "Loan4k", "Mature4k", "Old4k", "Pie4k", "Rim4k", "Shame4k", "Sis","Stuck4k", "Tutor4k", "Vip4k"]
                    bot.download_all_vip_channels_video()
                    videos_collection_dict = bot.vip4k_get_video()
                    bot.vip4k_download_video(videos_collection_dict)
                else :
                    SendAnEmail('Could not logged in into Vip 4k')
                
                bot.CloseDriver()
                if logggg == True:break
            except Exception as e :
                print(e)
                SendAnEmail(f'Got an error while processing the downloading process the videos!\nError : {e}')