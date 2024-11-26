from django.db import models
import os

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
    
    video = models.FileField(upload_to='videos',null=True,blank=True)
    image = models.FileField(upload_to='image',null=True,blank=True)
    Username = models.CharField(max_length=255,null=True,blank=True)
    Likes = models.IntegerField(null=True,blank=True)
    Disclike = models.IntegerField(null=True,blank=True)
    Url = models.URLField(null=True,blank=True)
    Title = models.CharField(max_length=255,null=True,blank=True)
    Discription = models.TextField(null=True,blank=True)
    Release_Date = models.CharField(max_length=255,null=True,blank=True)
    Poster_Image_url = models.URLField(null=True,blank=True)
    Video_name = models.CharField(max_length=255,null=True,blank=True)
    video_download_url = models.URLField(null=True,blank=True)
    Photo_name = models.CharField(max_length=255,null=True,blank=True)
    Pornstarts = models.TextField(null=True,blank=True)
    configuration = models.ForeignKey(configuration, on_delete=models.CASCADE, related_name='configuration',null=True,blank=True)
    cetegory = models.ForeignKey(cetegory, on_delete=models.CASCADE, related_name='cetegory',null=True,blank=True)