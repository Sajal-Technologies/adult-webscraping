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
                if bot.login_Handjob_TV():
                    logggg = True
                    bot.handjob_get_video()
                    bot.other_sites_of_handjob()
                else:
                    SendAnEmail('Could not logged in into Handjob TV')
                bot.CloseDriver()
                if logggg == True:break
                
            except Exception as e :
                print(e)
                SendAnEmail(f'Got an error while processing the downloading process the videos!\nError : {e}')