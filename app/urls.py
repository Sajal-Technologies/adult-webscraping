from django.urls import path
from django.conf.urls import include
from .views import download_file, list_csvs, download_csv, download_media_file

urlpatterns = [
    path('download_csv/<int:config_id>/<int:category_id>/', download_csv, name='download_csv'),
    path('csv/', list_csvs, name='list_csvs'),
    path('csv/download/<int:config_id>/', download_csv, name='download_csv'),
    path('media/download/<path:file_path>/', download_media_file, name='download_media_file'),
]