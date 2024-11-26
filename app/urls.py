from django.urls import path
from django.conf.urls import include
from .views import download_file, list_csvs, download_csv, download_media_file

urlpatterns = [
    path('downloads/<path:file_path>/', download_file, name='download_file'),
    path('csvs/', list_csvs, name='list_csvs'),
    path('csvs/download/<int:config_id>/', download_csv, name='download_csv'),
    path('media/download/<path:file_path>/', download_media_file, name='download_media_file'),

    # path('list_files/', list_files, name='list_file'),
    # path('csv/<str:file_name>', csv_file, name='csv_file'),
    # path('csv/', return_csv_links, name='csv_file_list'),
    # path('', data_flair),
    # path('API/', include('main.urls')),
    # path('run-script',RunScript.as_view(),name='RunScript')
]