from django.db import models
import os
from datetime import timedelta
from django.utils.timezone import now
from django.conf import settings

class RunScript(models.Model):
    datetime = models.IntegerField()
    last_run = models.DateTimeField(null=True,blank=True)
    def __str__(self):
        return f"RunScript at hour {self.datetime}"
    
# Create your models here.
class videos_collection(models.Model):
    Video_name = models.CharField(max_length=255,null=True, blank=True)
    Release_Date = models.DateTimeField(null=True,blank=True)
    Poster_Image_uri = models.URLField(null=True,blank=True)
    Poster_Image = models.FileField(upload_to='poster_imgs',null=True,blank=True)
    video = models.FileField(upload_to='videos')
    Likes = models.IntegerField(null=True,blank=True)
    Disclike = models.IntegerField(null=True,blank=True)
    Url = models.TextField(null=True,blank=True)
    Title = models.CharField(max_length=255)
    Discription = models.TextField(null=True,blank=True)
    Pornstarts = models.CharField(max_length=500,null=True,blank=True)
    Category = models.CharField(max_length=500,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.Video_name


class cetegory(models.Model):
    category = models.CharField(max_length=255,null=True,blank=True)
    link = models.URLField(null=True,blank=True)
    # configuration = models.ManyToManyField('configuration', related_name='configuration')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.category

class configuration(models.Model):
    website_name = models.CharField(max_length=255,null=True,blank=True)
    username = models.CharField(max_length=255,null=True,blank=True)
    password = models.CharField(max_length=255,null=True,blank=True)
    main_category = models.CharField(max_length=255,null=True,blank=True)
    category = models.ManyToManyField("cetegory", related_name='configurations',null=True,blank=True)
    more_than_old_days_download = models.IntegerField(null=True,blank=True)
    numbers_of_download_videos = models.IntegerField(null=True,blank=True)
    delete_old_days = models.IntegerField(null=True,blank=True)
    lastime_able_to_login_or_not = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.website_name

    
class send_mail(models.Model):
    email = models.EmailField(unique=True)
    
class sender_mail(models.Model):
    email = models.EmailField(unique=True)
    sender_password = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    server = models.CharField(max_length=255)
    port = models.IntegerField(default=0)
    
    
class VideosData(models.Model):
    
    video = models.FileField(upload_to='videos')
    image = models.FileField(upload_to='image')
    Username = models.CharField(max_length=255,null=True,blank=True)
    Likes = models.IntegerField(null=True,blank=True)
    Disclike = models.IntegerField(null=True,blank=True)
    Url = models.URLField(null=True,blank=True)
    Title = models.CharField(max_length=255,null=True,blank=True)
    Discription = models.TextField(null=True,blank=True)
    Release_Date = models.CharField(max_length=255,null=True,blank=True)
    Poster_Image_url = models.URLField(null=True,blank=True)
    Video_name = models.CharField(max_length=255,null=True,blank=True,unique=True)
    Photo_name = models.CharField(max_length=255,null=True,blank=True,unique=True)
    Pornstarts = models.TextField(null=True,blank=True)
    configuration = models.ForeignKey(configuration, on_delete=models.CASCADE, related_name='configuration',null=True,blank=True)
    cetegory = models.ForeignKey(cetegory, on_delete=models.CASCADE, related_name='cetegory',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_or_not = models.BooleanField(default=False)
    
    @classmethod
    def delete_older_videos(cls):
        """
        Deletes records older than the specified number of days along with their video and image files.

        Parameters:
            days (int): Number of days to check for old records.
        """
        # Delete files for records older than the cutoff
        old_records = cls.objects.filter(deleted_or_not = False)
        
        for record in old_records:
            try :
                # Get the `delete_old_days` value from the configuration
                days = record.configuration.delete_old_days if record.configuration else 0
                cutoff_date = now() - timedelta(days=days)

                # Check if the record is older than the cutoff date
                if record.created_at < cutoff_date:
                    # Delete associated video file
                    if record.video and os.path.exists(record.video.path):
                        os.remove(record.video.path)
                        print(f"Deleted video file: {record.video.path}")

                    # Delete associated image file
                    if record.image and os.path.exists(record.image.path):
                        os.remove(record.image.path)
                        print(f"Deleted image file: {record.image.path}")

                    # Delete the record
                    record.deleted_or_not = True
                    record.save()
                    print(f"Deleted record: {record.id}")
            except : ...

        # Get all valid file paths in the database
        valid_files = set()
        for record in cls.objects.all():
            try :
            
                if record.video:
                    valid_files.add(record.video.path)
                if record.image:
                    valid_files.add(record.image.path)
                
            except : ...
            

        # Delete orphaned files in the media folder
        try :
        
            media_root = settings.MEDIA_ROOT
            for root, _, files in os.walk(media_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in valid_files:
                        try:
                            os.remove(file_path)
                            print(f"Deleted orphaned file: {file_path}")
                        except Exception as e:
                            print(f"Error deleting file {file_path}: {e}")
        except : ...
        
        
        # old_records = cls.objects.all()
        # for record in old_records: 
        #     days = record.configuration.delete_old_days
        #     cutoff_date = now() - timedelta(days=days)
            
        #     if record.created_at < cutoff_date :
            
        #         # Delete associated video file
        #         if record.video and os.path.exists(record.video.path):
        #             os.remove(record.video.path)
        #             print(f"Deleted video file: {record.video.path}")

        #         # Delete associated image file
        #         if record.image and os.path.exists(record.image.path):
        #             os.remove(record.image.path)
        #             print(f"Deleted image file: {record.image.path}")

        #         # Delete the record
        #         record.delete()
        #         print(f"Deleted record: {record.id}")
