# avatars/management/commands/seed_avatars.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from authentication.models import Avatar
from django.core.files import File

class Command(BaseCommand):
    help = 'Seed avatars from a predefined directory'

    def handle(self, *args, **kwargs):
        # Define the directory path where images are stored
        directory = os.path.join(settings.BASE_DIR, 'static', 'avatars')
        
        # Check if the directory exists
        if not os.path.isdir(directory):
            self.stdout.write(self.style.ERROR(f'The directory "{directory}" does not exist.'))
            return

        # List all files in the directory
        image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        if not image_files:
            self.stdout.write(self.style.WARNING(f'No image files found in "{directory}".'))
            return

        # Iterate over each file and create Avatar entries
        for image_name in image_files:
            # Check if the file has a common image extension
            if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_url= os.path.join(settings.STATIC_URL, 'avatars', image_name)
                image_url = image_url.replace(' ', '%20')
                avatar, created = Avatar.objects.get_or_create(image_url=image_url)
                if not created:
                    self.stdout.write(self.style.WARNING(f'Avatar "{image_name}" already exists.'))
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded avatars.'))
