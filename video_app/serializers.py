from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'file_path', 
            'thumbnail', 'thumbnail_url', 'created_at', 
            'updated_at', 'user', 'username', 'views', 
            'file_size'
        ]
        read_only_fields = ['user', 'views', 'file_size']
    
    def get_file_size(self, obj):
        return obj.get_file_size()
    
    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and instance.file_path:
            representation['file_path'] = request.build_absolute_uri(instance.file_path.url)
        return representation
    
    def validate_file_path(self, value):
        # Validate file type
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        ext = value.name.lower().split('.')[-1]
        if f'.{ext}' not in valid_extensions:
            raise serializers.ValidationError(
                'Unsupported file format. Please upload MP4, AVI, MOV, or MKV files.'
            )
        # Validate file size (e.g., max 500MB)
        if value.size > 524288000:  # 500MB in bytes
            raise serializers.ValidationError(
                'File size too large. Maximum size is 500MB.'
            )
        return value
    