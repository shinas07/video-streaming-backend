from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Video

# ✅ Base Test Class to Avoid Duplication
class BaseTestSetup:
    def setUp(self):
        """Common setup for all tests"""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

# ✅ Video Model Tests (inherits BaseTestSetup)
class VideoTests(TestCase, BaseTestSetup):
    def test_create_video(self):
        """Test creating a video"""
        video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            user=self.user
        )
        self.assertEqual(video.title, 'Test Video')

# ✅ Video API Tests (inherits BaseTestSetup)
class VideoAPITests(APITestCase, BaseTestSetup):
    def setUp(self):
        """Call BaseTestSetup and authenticate user"""
        super().setUp()  # Call parent setUp
        self.client.force_authenticate(user=self.user)

    def test_upload_video(self):
        """Test video upload API"""
        data = {
            'title': 'Test Video',
            'description': 'Test Description'
        }
        response = self.client.post('/api/videos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
