import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from video_app.models import Video
from video_app.streaming import StreamManager
User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    user = User.objects.create_user(username='testuser',email='testuser@gamil.com',password='testpassword')
    return user

@pytest.fixture
def create_video(create_user, db):
    video = Video.objects.create(
        title='Test Video',
        description='Test Description',
        file_path=SimpleUploadedFile("test.mp4", b"file_content", content_type="video/mp4"),
          user=create_user,
        views=10
    )
    return video

def test_get_queryset(api_client, create_user, create_video):
    api_client.force_authenticate(user=create_user)
    response = api_client.get('/api/videos/')
    assert response.status_code == 200
    assert len(response.data) == 1

def test_perform_create(api_client, create_user):
    api_client.force_authenticate(user=create_user)
    video_data = {
        'title': 'New Video',
        'description': 'New Video Description',
        'file_path': SimpleUploadedFile("new.mp4", b"new_file_content", content_type="video/mp4")
    }
    response = api_client.post('/api/videos/', video_data, format='multipart')
    assert response.status_code == 201

def test_my_videos(api_client, create_user, create_video):
    api_client.force_authenticate(user=create_user)
    response = api_client.get('/api/videos/my_videos/')
    assert response.status_code == 200
    assert len(response.data) == 1

def test_stream_video(api_client, create_video):
    response = api_client.get(f'/api/videos/stream/{create_video.id}/')
    assert response.status_code in [200, 404] 

def test_stop_stream(api_client, create_video):
    StreamManager.get_instance().get_stream(create_video.id, create_video.file_path.path)
    response = api_client.post(f'/api/videos/{create_video.id}/stop-stream/')
    assert response.status_code == 200
