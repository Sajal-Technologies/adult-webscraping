from django.contrib import admin
from .models import VideosData, send_mail, sender_mail, configuration, cetegory, RunScript

admin.site.register(send_mail)
admin.site.register(sender_mail)
# admin.site.register(cetegory)

from django.contrib import admin
from .models import VideosData

@admin.register(VideosData)
class VideosDataAdmin(admin.ModelAdmin):
    list_display = ('Video_name','created_at', 'Username', 'video', 'image')  # Include created_at here
    list_filter = ('created_at',)  # Optional: Add filter for created_at
    search_fields = ('Username', 'video')  # Optional: Add search fields

@admin.register(configuration)
class VideosDataAdmin(admin.ModelAdmin):
    list_display = ('website_name','lastime_able_to_login_or_not', 'username', 'password')
    search_fields = ('lastime_able_to_login_or_not','website_name')
    
@admin.register(cetegory)
class VideosDataAdmin(admin.ModelAdmin):
    list_display = ('category','link')
    
@admin.register(RunScript)
class VideosDataAdmin(admin.ModelAdmin):
    list_display = ('datetime',)
