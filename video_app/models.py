from django.db import models
from django.conf import settings
from django.utils.text import slugify
import os
import uuid


class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file_path = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Create base slug from title
            base_slug = slugify(self.title)
            
            # Check if slug exists
            if Video.objects.filter(slug=base_slug).exists():
                # Add random suffix
                suffix = str(uuid.uuid4())[:6]
                self.slug = f"{base_slug}-{suffix}"
            else:
                self.slug = base_slug
                
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

    def get_file_size(self):
        if self.file_path:
            file_path = self.file_path.path  # Get absolute path
            if os.path.exists(file_path):  
                return os.path.getsize(file_path)  
        return 

    def get_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return None
