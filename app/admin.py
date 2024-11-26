from django.contrib import admin
from .models import VideosData, send_mail, sender_mail, configuration, cetegory
# Register your models here.

admin.site.register(VideosData)
admin.site.register(send_mail)
admin.site.register(sender_mail)
admin.site.register(configuration)
admin.site.register(cetegory)
