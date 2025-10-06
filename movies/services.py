from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Booking, Show
from common.exceptions import BookingError


class BookingService:
    """
    Service class to handle booking-related business logic.
    """

    @staticmethod
    @transaction.atomic
    def create_booking(user, show, seat_number):
        """
        Create a new booking with proper validation and error handling.

        Args:
            user: The user making the booking
            show: The show to book
            seat_number: The seat number to book

        Returns:
            Booking: The created booking instance

        Raises:
            BookingError: If booking cannot be created
        """
        try:
            # Validate show timing
            if show.date_time <= timezone.now():
                raise BookingError("Cannot book seats for past shows.")

            # Check if show is fully booked
            if show.is_fully_booked:
                raise BookingError("This show is fully booked.")

            # Check for existing booking
            existing_booking = Booking.objects.select_for_update().filter(
                show=show,
                seat_number=seat_number.upper(),
                status='booked'
            ).first()

            if existing_booking:
                raise BookingError(f"Seat {seat_number} is already booked.")

            # Create the booking
            booking = Booking(
                user=user,
                show=show,
                seat_number=seat_number.upper(),
                status='booked'
            )

            # Validate the booking
            booking.full_clean()
            booking.save()

            return booking

        except ValidationError as e:
            raise BookingError(f"Invalid booking data: {e}")
        except Exception as e:
            if isinstance(e, BookingError):
                raise
            raise BookingError(f"Failed to create booking: {str(e)}")

    @staticmethod
    def cancel_booking(booking):
        """
        Cancel an existing booking.

        Args:
            booking: The booking to cancel

        Returns:
            Booking: The cancelled booking instance

        Raises:
            BookingError: If booking cannot be cancelled
        """
        try:
            if booking.status == 'cancelled':
                raise BookingError("Booking is already cancelled.")

            if not booking.can_be_cancelled:
                raise BookingError("Cannot cancel booking for past shows.")

            booking.cancel()
            return booking

        except Exception as e:
            if isinstance(e, BookingError):
                raise
            raise BookingError(f"Failed to cancel booking: {str(e)}")

    @staticmethod
    def get_seat_availability(show):
        """
        Get seat availability information for a show.

        Args:
            show: The show to check

        Returns:
            dict: Dictionary with availability information
        """
        booked_seats = show.get_booked_seat_numbers()
        total_seats = show.total_seats
        available_seats = show.available_seats

        return {
            'total_seats': total_seats,
            'available_seats': available_seats,
            'booked_seats': booked_seats,
            'is_fully_booked': show.is_fully_booked
        }

    @staticmethod
    def validate_seat_number(seat_number, show=None):
        """
        Validate seat number format and availability.

        Args:
            seat_number: The seat number to validate
            show: Optional show to check availability against

        Returns:
            str: Normalized seat number

        Raises:
            BookingError: If seat number is invalid
        """
        if not seat_number or not seat_number.strip():
            raise BookingError("Seat number cannot be empty.")

        seat_number = seat_number.strip().upper()

        # Basic format validation (A1, B2, etc.)
        if not (len(seat_number) >= 2 and seat_number[0].isalpha() and seat_number[1:].isdigit()):
            raise BookingError("Invalid seat number format. Use format like A1, B2, etc.")

        # Row validation (A-Z)
        seat_row = seat_number[0]
        if seat_row < 'A' or seat_row > 'Z':
            raise BookingError("Invalid seat row. Must be A-Z.")

        # Number validation (1-99)
        try:
            seat_num = int(seat_number[1:])
            if seat_num < 1 or seat_num > 99:
                raise BookingError("Invalid seat number. Must be 1-99.")
        except ValueError:
            raise BookingError("Invalid seat number format.")

        # If show is provided, check availability
        if show:
            booked_seats = show.get_booked_seat_numbers()
            if seat_number in booked_seats:
                raise BookingError(f"Seat {seat_number} is already booked.")

        return seat_number


class ShowService:
    """
    Service class to handle show-related business logic.
    """

    @staticmethod
    def get_available_shows(movie_id=None):
        """
        Get available shows, optionally filtered by movie.

        Args:
            movie_id: Optional movie ID to filter by

        Returns:
            QuerySet: Available shows
        """
        shows = Show.objects.filter(
            date_time__gte=timezone.now()
        ).select_related('movie')

        if movie_id:
            shows = shows.filter(movie_id=movie_id, movie__is_active=True)
        else:
            shows = shows.filter(movie__is_active=True)

        return shows.order_by('date_time')

    @staticmethod
    def get_show_statistics(show):
        """
        Get statistics for a show.

        Args:
            show: The show to get statistics for

        Returns:
            dict: Show statistics
        """
        total_bookings = show.bookings.count()
        active_bookings = show.bookings.filter(status='booked').count()
        cancelled_bookings = show.bookings.filter(status='cancelled').count()

        return {
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'cancelled_bookings': cancelled_bookings,
            'available_seats': show.available_seats,
            'occupancy_rate': (active_bookings / show.total_seats * 100) if show.total_seats > 0 else 0
        }
