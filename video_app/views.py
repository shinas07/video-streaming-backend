from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Video
from .serializers import VideoSerializer
import logging

logger = logging.getLogger(__name__)

class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return all videos for listing, but only user's videos for editing
        if self.action in ['list', 'retrieve']:
            return Video.objects.all()
        return Video.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        logger.info(f"Video created: {serializer.data['title']} by {self.request.user.email}")
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if query:
            videos = Video.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            serializer = self.get_serializer(videos, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        video = self.get_object()
        video.views += 1
        video.save()
        return Response({'views': video.views})
