from django.core.management.base import BaseCommand, CommandError
from main.models import configuration as conf
from scrapping.settings import BASE_DIR
from mail import SendAnEmail
from bot import scrapping_bot
from main.models import send_mail

class Command(BaseCommand):
    help = "Closes the specified poll for voting"


    def handle(self, *args, **options): 
        # try:
            emailss = [mail.email for mail in send_mail.objects.all()]
            bot = scrapping_bot()

            if  bot.fivekteen_login():
                bot.download_fivek_teen_video()
                bot.download_fivek_porn_video()
            else:
                SendAnEmail('Could not login into 5kteen!',email=emailss)
            
            ...
        # except Exception as e :
        #         SendAnEmail(f'Got an error while processing the downloading process the videos of naughty america!\nError : {e}')