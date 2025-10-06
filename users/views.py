from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer


@swagger_auto_schema(
    method='post',
    request_body=UserRegistrationSerializer,
    responses={
        201: openapi.Response('User created successfully', UserSerializer),
        400: 'Bad request'
    },
    operation_description="Register a new user account"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    Register a new user account.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user_serializer = UserSerializer(user)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'User created successfully',
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    return Response({
        'error': 'Registration failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            'Login successful',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'access': openapi.Schema(type=openapi.TYPE_STRING),
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        401: 'Invalid credentials'
    },
    operation_description="Login user and get JWT tokens"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and return JWT tokens.
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)

            return Response({
                'message': 'Login successful',
                'user': user_serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        'error': 'Invalid input',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: UserSerializer},
    operation_description="Get current user profile",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Get current user profile.
    """
    serializer = UserSerializer(request.user)
    return Response({
        'user': serializer.data
    }, status=status.HTTP_200_OK)
