from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
import logging
from rest_framework import serializers

logger = logging.getLogger('django')
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        try:
            
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            logger.info(f"User registered successfully: {user.email}")
            response_data = {
                'status': 'success',
                'message': 'Registration successful. Please login to continue.',
                'user': {
                    'email': user.email,
                    'username': user.username
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            # Log validation errors in detail
            logger.error(f"Validation error during registration: {serializer.errors}")
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error during registration: {str(e)}")
            logger.error(f"Request data was: {request.data}")
            return Response({
                'status': 'error',
                'message': 'Registration failed',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                user = authenticate(email=email,password=password)

                if user is None:
                    return Response({'status':'error','message':'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
                
                if not user.is_active:
                    return Response({
                        'status': 'error',
                        'message': 'Account is disabled'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                refresh = RefreshToken.for_user(user)

                return Response({
                'status': 'success',
                'message': 'Login successful',
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({
                'status': 'error',
                'message': 'Login failed',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                logger.warning(f"Logout attempted without refresh token by user:")
                return Response(
                    {'error': 'Refresh token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get token object
            token = RefreshToken(refresh_token)
            
            # Blacklist the refresh token
            token.blacklist()
            
            logger.info("User logged out successfully")
            return Response(
                {
                    'status': 'success',
                    'message': 'Successfully logged out'
                }, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Logout error for {str(e)}")
            return Response(
                {
                    'status': 'error',
                    'message': 'Invalid token or token has expired'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
            