from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Movie, Show, Booking


class MovieSerializer(serializers.ModelSerializer):
    shows_count = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'duration_minutes', 'description', 'genre', 
                 'rating', 'release_date', 'is_active', 'shows_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'shows_count']

    def get_shows_count(self, obj):
        return obj.shows.filter(date_time__gte=timezone.now()).count()


class ShowSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_duration = serializers.IntegerField(source='movie.duration_minutes', read_only=True)
    available_seats = serializers.ReadOnlyField()
    is_fully_booked = serializers.ReadOnlyField()
    booked_seat_numbers = serializers.SerializerMethodField()

    class Meta:
        model = Show
        fields = ['id', 'movie', 'movie_title', 'movie_duration', 'screen_name', 
                 'date_time', 'total_seats', 'available_seats', 'is_fully_booked',
                 'price', 'booked_seat_numbers', 'created_at']
        read_only_fields = ['id', 'created_at', 'available_seats', 'is_fully_booked', 'booked_seat_numbers']

    def get_booked_seat_numbers(self, obj):
        return obj.get_booked_seat_numbers()

    def validate_date_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Show time must be in the future.")
        return value


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['seat_number']

    def validate_seat_number(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Seat number cannot be empty.")

        # Basic seat number format validation (A1, B2, etc.)
        if not (len(value) >= 2 and value[0].isalpha() and value[1:].isdigit()):
            raise serializers.ValidationError("Invalid seat number format. Use format like A1, B2, etc.")

        return value.strip().upper()

    def validate(self, attrs):
        show = self.context.get('show')
        seat_number = attrs.get('seat_number')
        user = self.context.get('request').user

        if not show:
            raise serializers.ValidationError("Show is required.")

        # Check if show time has passed
        if show.date_time <= timezone.now():
            raise serializers.ValidationError("Cannot book seats for past shows.")

        # Check if seat is already booked
        existing_booking = Booking.objects.filter(
            show=show,
            seat_number=seat_number,
            status='booked'
        ).first()

        if existing_booking:
            raise serializers.ValidationError(f"Seat {seat_number} is already booked.")

        # Check if show is fully booked
        if show.is_fully_booked:
            raise serializers.ValidationError("This show is fully booked.")

        # Basic seat range validation (assuming seats are A1-Z99)
        seat_row = seat_number[0]
        seat_num = int(seat_number[1:])

        if seat_row < 'A' or seat_row > 'Z':
            raise serializers.ValidationError("Invalid seat row. Must be A-Z.")

        if seat_num < 1 or seat_num > 99:
            raise serializers.ValidationError("Invalid seat number. Must be 1-99.")

        return attrs

    def create(self, validated_data):
        show = self.context.get('show')
        user = self.context.get('request').user

        booking = Booking.objects.create(
            user=user,
            show=show,
            **validated_data
        )
        return booking


class BookingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    movie_title = serializers.CharField(source='show.movie.title', read_only=True)
    show_date_time = serializers.DateTimeField(source='show.date_time', read_only=True)
    screen_name = serializers.CharField(source='show.screen_name', read_only=True)
    can_be_cancelled = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = ['id', 'user_username', 'movie_title', 'show_date_time', 
                 'screen_name', 'seat_number', 'status', 'booking_reference', 
                 'can_be_cancelled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'booking_reference', 'created_at', 'updated_at']


class BookingCancelSerializer(serializers.Serializer):
    def validate(self, attrs):
        booking = self.instance

        if not booking:
            raise serializers.ValidationError("Booking not found.")

        if booking.status == 'cancelled':
            raise serializers.ValidationError("Booking is already cancelled.")

        if not booking.can_be_cancelled:
            raise serializers.ValidationError("Cannot cancel booking for past shows.")

        return attrs

    def update(self, instance, validated_data):
        instance.cancel()
        return instance


class ShowDetailSerializer(ShowSerializer):
    movie = MovieSerializer(read_only=True)
    bookings_count = serializers.SerializerMethodField()

    class Meta(ShowSerializer.Meta):
        fields = ShowSerializer.Meta.fields + ['movie', 'bookings_count']

    def get_bookings_count(self, obj):
        return obj.bookings.filter(status='booked').count()
