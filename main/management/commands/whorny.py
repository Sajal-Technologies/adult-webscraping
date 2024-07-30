from django.core.management.base import BaseCommand, CommandError
from main.models import configuration as conf
from mail import SendAnEmail

class Command(BaseCommand):
    help = "Closes the specified poll for voting"


    def handle(self, *args, **options): 
        from bot import scrapping_bot
        logggg = False
        for _ in range(1):
            try:
                bot = scrapping_bot()
                driver = bot.starting_bots()
                if not driver:
                    SendAnEmail('Could not open up the driver')
                    return

                print('whorny process starting')
                if bot.whorny_login():
                    logggg = True
                    bot.download_whorny_videos()
                else :
                    SendAnEmail('Could not logged in into Adult prime')

                bot.CloseDriver()
                if logggg == True:break
                
            except Exception as e :
                print(e)
                SendAnEmail(f'Got an error while processing the downloading process the videos!\nError : {e}')