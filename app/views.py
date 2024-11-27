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
from .models import VideosData, configuration, cetegory, RunScript
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import FileResponse

def generate_csv(configuration_obj, category_obj, request, is_main_category=False):
    """
    Generates a CSV file for the given configuration and category and returns it as an HTTP response.
    
    Parameters:
        configuration: The configuration object to filter video data.
        category: The category object to filter video data.
        request: The HTTP request object for generating absolute URLs.
        is_main_category: Boolean flag to indicate if the CSV is for the main category (no specific category)
    
    Returns:
        HttpResponse: The CSV file as an attachment.
    """
    # If is_main_category is True, fetch videos for the entire configuration (without filtering by category)
    if is_main_category:
        if not  category_obj:
            category_obj = cetegory.objects.filter(category = configuration_obj.main_category)
        if category_obj :
            category_obj = category_obj.first()
            videos = VideosData.objects.filter(configuration=configuration_obj, cetegory=category_obj)
        else :
            videos = VideosData.objects.filter(configuration=configuration_obj, cetegory=None)
            
    else:
        # Otherwise, filter by both configuration and specific category
        videos = VideosData.objects.filter(configuration=configuration_obj, cetegory=category_obj)
    
    # Prepare data for the DataFrame
    data = []
    for video in videos:
        video_download_link = request.build_absolute_uri(reverse('download_media_file', args=[video.video.name])) if video.video else ''
        image_download_link = request.build_absolute_uri(reverse('download_media_file', args=[video.image.name])) if video.image else ''
        
        data.append({
            'Direct Video Download Link': video_download_link,
            'Direct Image Download Link': image_download_link,
            'Video Name': video.Video_name,
            'Photo Name': video.Photo_name,
            'Title': video.Title,
            'Description': video.Discription,
            'Pornstars': video.Pornstarts,
            'Category': video.cetegory.category if video.cetegory else 'No Category',  # Handle category being None
            'Main Category': configuration_obj.main_category,  # Add main_category to data
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
    
    # Set the filename based on whether it's for the main category or specific category
    if is_main_category:
        response['Content-Disposition'] = f'attachment; filename="{configuration_obj.website_name}_{configuration_obj.main_category}_main_category_{now().strftime("%Y%m%d%H%M%S")}.csv"'
    else:
        response['Content-Disposition'] = f'attachment; filename="{configuration_obj.website_name}_{configuration_obj.main_category}_{category_obj.category}_{now().strftime("%Y%m%d%H%M%S")}.csv"'

    df.to_csv(response, index=False)  # Write DataFrame to the response object

    return response

def download_csv(request, config_id, category_id=None):
    """
    Generates a CSV file for the given configuration and category and returns it as an HTTP response.
    
    Parameters:
        request: The HTTP request object.
        config_id: The ID of the configuration.
        category_id: The ID of the category (optional).
    
    Returns:
        HttpResponse: The CSV file as an attachment.
    """
    config = get_object_or_404(configuration, id=config_id)

    # If category_id is provided, generate CSV for that specific category
    if category_id:
        category = get_object_or_404(cetegory, id=category_id)
        return generate_csv(config, category, request)

    # If category_id is not provided, generate CSV for the main category (no specific category filter)
    return generate_csv(config, None, request, is_main_category=True)

from datetime import datetime, timedelta
from django.utils import timezone

def list_csvs(request):
    configs = configuration.objects.all()
    data = []

    def get_next_run_time():
        # Assuming you have only one entry in RunScript
        run_script = RunScript.objects.first()

        # Get the current time in UTC (or your desired timezone)
        current_datetime = timezone.now()

        # Calculate the next run time by adding the datetime interval to last_run
        next_run_time = run_script.last_run + timedelta(hours=run_script.datetime)

        # If the next run time is in the future, return that time. Otherwise, calculate the next possible run time.
        if next_run_time > current_datetime:
            return next_run_time
        else:
            # If the next run time has already passed, schedule the next run at a future time.
            return current_datetime + timedelta(hours=run_script.datetime)
        
    next_run = get_next_run_time()
    
    # Loop through all configurations
    for config in configs:
        
        # Add download links for all categories associated with the configuration
        for category in config.category.all():
            videos_data = VideosData.objects.filter(configuration=config, cetegory=category)
            if videos_data :
                number_of_videos = videos_data.count()
                last_download = videos_data.last().created_at.strftime('%b %d, %Y at %I %p')
                formatted_next_run = next_run.strftime('%b %d, %Y at %I:%M %p')
            else:
                number_of_videos = ""
                last_download = ""
                formatted_next_run = ""
            data.append({
                'config': config,
                'category': category,
                'download_link': reverse('download_csv', args=[config.id, category.id]), 
                'number_of_videos': number_of_videos, 
                'Last_downloaded_videos': last_download, 
                'formatted_next_run': formatted_next_run, 
            })

    return render(request, 'list_csvs.html', {'data': data})

def download_media_file(request, file_path):
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    if not os.path.exists(full_path):
        return HttpResponse("File not found.", status=404)

    response = FileResponse(open(full_path, 'rb'), as_attachment=True)
    return response