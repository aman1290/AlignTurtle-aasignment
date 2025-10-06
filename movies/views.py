from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Movie, Show, Booking
from .serializers import (
    MovieSerializer, ShowSerializer, ShowDetailSerializer,
    BookingSerializer, BookingCreateSerializer, BookingCancelSerializer
)
from .services import BookingService
from common.exceptions import BookingError


# Movie Views
@swagger_auto_schema(
    method='get',
    responses={200: MovieSerializer(many=True)},
    operation_description="Get list of all active movies"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list(request):
    """
    Get list of all active movies.
    """
    movies = Movie.objects.filter(is_active=True).order_by('title')
    serializer = MovieSerializer(movies, many=True)
    return Response({
        'count': len(serializer.data),
        'movies': serializer.data
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    responses={
        200: ShowSerializer(many=True),
        404: 'Movie not found'
    },
    operation_description="Get list of shows for a specific movie"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def movie_shows(request, movie_id):
    """
    Get list of shows for a specific movie.
    """
    movie = get_object_or_404(Movie, id=movie_id, is_active=True)

    # Filter shows that haven't started yet
    shows = Show.objects.filter(
        movie=movie,
        date_time__gte=timezone.now()
    ).order_by('date_time')

    serializer = ShowSerializer(shows, many=True)
    return Response({
        'movie': MovieSerializer(movie).data,
        'count': len(serializer.data),
        'shows': serializer.data
    }, status=status.HTTP_200_OK)


# Show Views
@swagger_auto_schema(
    method='get',
    responses={200: ShowDetailSerializer},
    operation_description="Get detailed information about a show",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <token> (optional for show details)",
            type=openapi.TYPE_STRING,
            required=False
        )
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def show_detail(request, show_id):
    """
    Get detailed information about a show.
    """
    show = get_object_or_404(Show, id=show_id)
    serializer = ShowDetailSerializer(show)
    return Response({
        'show': serializer.data
    }, status=status.HTTP_200_OK)


# Booking Views
@swagger_auto_schema(
    method='post',
    request_body=BookingCreateSerializer,
    responses={
        201: BookingSerializer,
        400: 'Bad request',
        404: 'Show not found'
    },
    operation_description="Book a seat for a show",
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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_seat(request, show_id):
    """
    Book a seat for a show.
    """
    show = get_object_or_404(Show, id=show_id)

    serializer = BookingCreateSerializer(
        data=request.data,
        context={'show': show, 'request': request}
    )

    if serializer.is_valid():
        try:
            with transaction.atomic():
                booking = BookingService.create_booking(
                    user=request.user,
                    show=show,
                    seat_number=serializer.validated_data['seat_number']
                )

                response_serializer = BookingSerializer(booking)
                return Response({
                    'message': 'Seat booked successfully',
                    'booking': response_serializer.data
                }, status=status.HTTP_201_CREATED)

        except BookingError as e:
            return Response({
                'error': 'Booking failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Booking failed',
                'details': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'error': 'Invalid booking data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    responses={
        200: BookingSerializer,
        400: 'Bad request',
        403: 'Permission denied',
        404: 'Booking not found'
    },
    operation_description="Cancel a booking",
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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    """
    Cancel a booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if user owns this booking
    if booking.user != request.user:
        return Response({
            'error': 'Permission denied',
            'details': 'You can only cancel your own bookings'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = BookingCancelSerializer(booking, data={})

    if serializer.is_valid():
        try:
            booking = BookingService.cancel_booking(booking)
            response_serializer = BookingSerializer(booking)

            return Response({
                'message': 'Booking cancelled successfully',
                'booking': response_serializer.data
            }, status=status.HTTP_200_OK)

        except BookingError as e:
            return Response({
                'error': 'Cancellation failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'error': 'Cancellation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: BookingSerializer(many=True)},
    operation_description="Get list of user's bookings",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <token>",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description="Filter by booking status (booked/cancelled)",
            type=openapi.TYPE_STRING,
            required=False
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    """
    Get list of current user's bookings.
    """
    bookings = Booking.objects.filter(user=request.user).select_related(
        'show', 'show__movie'
    ).order_by('-created_at')

    # Filter by status if provided
    status_filter = request.query_params.get('status')
    if status_filter in ['booked', 'cancelled']:
        bookings = bookings.filter(status=status_filter)

    serializer = BookingSerializer(bookings, many=True)
    return Response({
        'count': len(serializer.data),
        'bookings': serializer.data
    }, status=status.HTTP_200_OK)


# Additional utility views
@swagger_auto_schema(
    method='get',
    responses={200: ShowSerializer(many=True)},
    operation_description="Get list of all upcoming shows"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def upcoming_shows(request):
    """
    Get list of all upcoming shows.
    """
    shows = Show.objects.filter(
        date_time__gte=timezone.now(),
        movie__is_active=True
    ).select_related('movie').order_by('date_time')

    serializer = ShowSerializer(shows, many=True)
    return Response({
        'count': len(serializer.data),
        'shows': serializer.data
    }, status=status.HTTP_200_OK)
