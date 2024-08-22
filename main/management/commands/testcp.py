# https://www.google.com/recaptcha/api2/demo
from django.core.management.base import BaseCommand, CommandError
from main.models import configuration as conf, videos_collection
from scrapping.settings import BASE_DIR
from mail import SendAnEmail
from bot import scrapping_bot
from main.models import send_mail


class Command(BaseCommand):
    help = "Closes the specified poll for voting"


    def handle(self, *args, **options):
        obj = videos_collection.objects.all().first()
        obj.video.url
