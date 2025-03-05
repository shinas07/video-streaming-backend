from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_path = models.FileField(upload_to='video/')
    thumbnail = models.ImageField(upload_to='thumbnails/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
