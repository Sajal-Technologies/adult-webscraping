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
            if  bot.sexmex_login():
                bot.sexmax_video_download()
            else:
                SendAnEmail('Could not login into naughty america!',email=emailss)
            
            ...
        # except Exception as e :
        #         SendAnEmail(f'Got an error while processing the downloading process the videos of naughty america!\nError : {e}')