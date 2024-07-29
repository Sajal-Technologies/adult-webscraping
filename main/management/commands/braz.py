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
                # close_every_chrome()
                bot = scrapping_bot(brazzers_bot=True)

                driver = bot.starting_bots()
                if not driver :
                    SendAnEmail('Could not open up the driver')
                    return
                if bot.brazzers_login() :
                    logggg = True
                    breakpoint()
                    video_dict = bot.get_brazzers_videos_url()
                    bot.download_brazzer_videos(video_dict)

                    # bot.brazzers_download_video(video_dict)  # don't uncomment this line 

                    bot.download_all_brazzer_channels_video()
                else:
                    SendAnEmail('Could not logged in into Brazzers')
                bot.CloseDriver()
                if logggg == True:break
                
            except Exception as e :
                print(e)
                SendAnEmail(f'Got an error while processing the downloading process the videos!\nError : {e}')