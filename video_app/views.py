from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from .streaming import StreamManager
from django.http import StreamingHttpResponse, HttpResponseServerError, FileResponse
from django.db.models import Q
from .models import Video
from .serializers import VideoSerializer
import logging
from wsgiref.util import FileWrapper
from django.conf import settings
from functools import wraps

logger = logging.getLogger(__name__)

class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Video.objects.all()
        
        # Get query parameters
        search_query = self.request.query_params.get('search', None)
        sort_by = self.request.query_params.get('sort', 'newest')

        # Apply search filter if search query exists
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(user__username__icontains=search_query)
            )

        # Apply sorting
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-views')
        else:
            queryset = queryset.order_by('-created_at')  

        return queryset
    
    def perform_create(self, serializer):
        """Save a new video with the requesting user as the owner."""
        serializer.save(user=self.request.user)
        logger.info(f"Video created: {serializer.data['title']} by {self.request.user.email}")
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search videos by title or description based on the query parameter."""
        query = request.query_params.get('q', '')
        if query:
            videos = Video.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            serializer = self.get_serializer(videos, many=True)
            return Response(serializer.data)
        return Response([])
    
    # @action(detail=True, methods=['post'])
    # def increment_views(self, request, pk=None):
    #     """increment the view count of a specific video by 1."""
    #     video = self.get_object()
    #     video.views += 1
    #     video.save()
    #     return Response({'views': video.views})
    
    @action(detail=False, methods=['GET'])
    def my_videos(self, request):
        """Get videos uploaded by the current user"""
        videos = Video.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)

def with_stream_cleanup(view_func):
    """Decorator to ensure stream cleanup"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        stream = None
        try:
            return view_func(request, *args, **kwargs)
        finally:
            if stream:
                try:
                    StreamManager.get_instance().release_stream(kwargs.get('video_id'))
                except Exception as e:
                    logger.error(f"Cleanup error: {str(e)}")
    return wrapper

@api_view(['GET'])
@with_stream_cleanup
def stream_video(request, video_id):
    """Stream video using OpenCV"""
    stream = None
    try:
        video = Video.objects.get(id=video_id)
        stream_manager = StreamManager.get_instance()
        stream = stream_manager.get_stream(video_id, video.file_path.path)
        
        def frame_generator():
            try:
                while True:
                    frame = stream.get_frame()
                    if frame:
                        # print('frame add and sending')
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    else:
                        logger.warning('Frame not available')
                        break
            except Exception as e:
                logger.error(f"Frame generator error: {str(e)}")
            finally:
                try:
                    stream_manager.release_stream(video_id)
                except Exception as e:
                    logger.error(f"Stream cleanup error: {str(e)}")

        response = StreamingHttpResponse(
            frame_generator(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
        
        # Add CORS headers
        # response["Access-Control-Allow-Origin"] = "*"
        # response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        # response["Access-Control-Allow-Headers"] = "Accept, Content-Type, Authorization"
        
        return response

    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=404)
    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        if stream:
            try:
                stream_manager.release_stream(video_id)
            except Exception as cleanup_error:
                logger.error(f"Cleanup error: {str(cleanup_error)}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def stop_stream(request, video_id):
    """Stop video stream"""
    try:
        StreamManager.get_instance().release_stream(video_id)
        return Response({'status': 'success'})
    except Exception as e:
        logger.error(f"Error stopping stream: {str(e)}")
        return Response({'error': str(e)}, status=500)
