from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, stream_video, stop_stream

router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='video')

# The router will automatically create URLs for:
# /videos/ - GET (list), POST (create)
# /videos/{id}/ - GET (retrieve), PUT/PATCH (update), DELETE (delete)
# /videos/my_videos/ - GET (custom action)
# /videos/{id}/increment_views/ - POST (custom action)
# /videos/search/ - GET (custom action)

urlpatterns = [
    path('',include(router.urls)),
    path('videos/<int:video_id>/stream/', stream_video, name='stream-video'),
    path('videos/<int:video_id>/stop-stream/', stop_stream, name='stop-stream'),
]
