import os
from django.conf import settings

def clear_picture():
    media_root = settings.MEDIA_ROOT
    for file_name in os.listdir(media_root):
    # construct full file path
        file = media_root + file_name
        if os.path.isfile(file):
            print('Deleting file:', file)
            os.remove(file)