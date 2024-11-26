from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import Settings
from Scrape import settings
import os, pandas as pd
# Create your views here.



def download_file(request, file_path):
    # Construct the full path to the file using the MEDIA_ROOT setting.
    media_root = settings.MEDIA_ROOT
    file = os.path.join(media_root, file_path)
    file = os.path.join(media_root, file_path)
    os.path.exists(file)
    if os.path.basename(file).endswith('.csv'):file = os.path.join(os.getcwd(), file_path)
    # Check if the file exists.
    
    if not os.path.exists(file) :
        file = os.path.join(settings.BASE_DIR,'downloads', file_path)
        if not os.path.exists(file) : 
            return HttpResponse("File could not found or Folder is empty",status=200)
        
    if os.path.isfile(file):
        with open(file, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file)}"'
            return response
    
    elif os.path.isdir(file):
        file_links = []
        files = os.listdir(file)
        if not files: return HttpResponse("Folder is empty",status=200)
        for file in files:
            if file.endswith('.mp4') or file.endswith('.jpg') or 'video' in str(file):
                # file_path = os.path.join(static_root, file)
                file_links.append(f'<a href="/downloads/{file}/">{file}</a>')
            elif 'video' in str(file) and not file.endswith('.mp4') or not file.endswith('.jpg') and 'admin' not in str(file):
                file_links.append(f'<a href="/downloads/{file}/">{file}</a>')
        return HttpResponse("<br>".join(file_links))
    else:
        HttpResponse("Folder not found.", status=404)
        
        
        
import csv
from django.http import HttpResponse
from django.utils.timezone import now
from .models import VideosData, configuration
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import FileResponse

def generate_csv(configuration,request):
    """
    Generates a CSV file for the given configuration using pandas and returns it as an HTTP response.
    
    Parameters:
        configuration: The configuration object to filter video data.
        request: The HTTP request object for generating absolute URLs.

    Returns:
        HttpResponse: The CSV file as an attachment.
    """
    # Fetch video data for the configuration
    videos = VideosData.objects.filter(configuration=configuration)
    
    # Prepare data for the DataFrame
    data = []
    for video in videos:
        video_download_link = request.build_absolute_uri(reverse('download_media_file', args=[video.video.name])) if video.video else ''
        image_download_link = request.build_absolute_uri(reverse('download_media_file', args=[video.image.name])) if video.image else ''
        
        data.append({
            'Direct Video Download Link': video_download_link,
            'Direct Image Download Link': image_download_link,
            'Handjob Video Url': video.Url,
            'Video Name': video.Video_name,
            'Photo name': video.Photo_name,
            'Title': video.Title,
            'Discription': video.Discription,
            'Pornstarts': video.Pornstarts,
            'cetegory': video.cetegory.category,
            'Username': video.Username,
            'Likes': video.Likes,
            'Dislikes': video.Disclike,
            'Video URL': video.Url,
            'Image URL': video.Poster_Image_url,
            'Release Date': video.Release_Date,
        })

    # Create a pandas DataFrame
    df = pd.DataFrame(data)

    # Convert the DataFrame to CSV format
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{configuration.website_name}_{now().strftime("%Y%m%d%H%M%S")}.csv"'

    df.to_csv(response, index=False)  # Write DataFrame to the response object

    return response

def download_csv(request, config_id):
    config = get_object_or_404(configuration, id=config_id)

    return generate_csv(config,request)


def list_csvs(request):
    configs = configuration.objects.all()
    data = [
        {
            'config': config,
            'download_link': reverse('download_csv', args=[config.id])
        }
        for config in configs
    ]
    return render(request, 'list_csvs.html', {'data': data})

def download_media_file(request, file_path):
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    if not os.path.exists(full_path):
        return HttpResponse("File not found.", status=404)

    response = FileResponse(open(full_path, 'rb'), as_attachment=True)
    return response