from django.contrib import admin
from .models import VideosData, send_mail, sender_mail, configuration, cetegory
# Register your models here.

admin.site.register(send_mail)
admin.site.register(sender_mail)
admin.site.register(configuration)
admin.site.register(cetegory)

from django.contrib import admin
from .models import VideosData

@admin.register(VideosData)
class VideosDataAdmin(admin.ModelAdmin):
    list_display = ('Video_name','created_at', 'Username', 'video', 'image')  # Include created_at here
    list_filter = ('created_at',)  # Optional: Add filter for created_at
    search_fields = ('Username', 'video')  # Optional: Add search fields
