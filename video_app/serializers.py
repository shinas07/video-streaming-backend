from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'file_path', 
            'thumbnail', 'created_at', 'updated_at',
            'user', 'username', 'slug', 'views', 'file_size'
        ]
        read_only_fields = ['user', 'views', 'slug']
    
    def get_file_size(self, obj):
        if obj.file_path:
            return obj.file_path.size
        return None
    
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
    