from django.contrib import admin
from .models import videos_collection,configuration, send_mail, sender_mail
# Register your models here.

admin.site.register(configuration)
admin.site.register(send_mail)
admin.site.register(sender_mail)

@admin.register(videos_collection)
class VideosCollectionAdmin(admin.ModelAdmin):
    list_display = (
        'Category',
        'created_at'
    )
    list_filter = ('Release_Date', 'Category')
    search_fields = ('Video_name', 'Title', 'Category')