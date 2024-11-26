from django.core.management.base import BaseCommand
from app.models import VideosData
from utils.mail import SendAnEmail

class Command(BaseCommand):
    help = "Closes the specified poll for voting"
        
    def handle(self, *args, **options):
        VideosData.delete_older_videos()
        SendAnEmail(f"Checking weather email has been sent or not")
        
