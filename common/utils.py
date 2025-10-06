"""
Utility functions for the Movie Booking System.
"""
import string
import random
from datetime import datetime, timedelta
from django.utils import timezone


def generate_booking_reference():
    """
    Generate a unique booking reference.

    Returns:
        str: A unique booking reference
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))


def validate_seat_number_format(seat_number):
    """
    Validate the format of a seat number.

    Args:
        seat_number (str): The seat number to validate

    Returns:
        bool: True if format is valid, False otherwise
    """
    if not seat_number or not isinstance(seat_number, str):
        return False

    seat_number = seat_number.strip().upper()

    # Check basic format: Letter followed by numbers
    if len(seat_number) < 2:
        return False

    if not seat_number[0].isalpha():
        return False

    if not seat_number[1:].isdigit():
        return False

    # Check row is A-Z
    if seat_number[0] < 'A' or seat_number[0] > 'Z':
        return False

    # Check number is 1-99
    try:
        seat_num = int(seat_number[1:])
        if seat_num < 1 or seat_num > 99:
            return False
    except ValueError:
        return False

    return True


def normalize_seat_number(seat_number):
    """
    Normalize a seat number to standard format.

    Args:
        seat_number (str): The seat number to normalize

    Returns:
        str: Normalized seat number (uppercase, stripped)
    """
    if not seat_number:
        return ""
    return seat_number.strip().upper()


def is_show_bookable(show_datetime):
    """
    Check if a show is bookable (not in the past).

    Args:
        show_datetime (datetime): The show datetime

    Returns:
        bool: True if bookable, False otherwise
    """
    return show_datetime > timezone.now()


def get_show_status(show_datetime):
    """
    Get the status of a show based on its datetime.

    Args:
        show_datetime (datetime): The show datetime

    Returns:
        str: 'upcoming', 'ongoing', or 'past'
    """
    now = timezone.now()

    if show_datetime > now:
        return 'upcoming'
    elif show_datetime <= now < show_datetime + timedelta(hours=3):  # Assuming 3-hour buffer
        return 'ongoing'
    else:
        return 'past'


def format_duration(minutes):
    """
    Format duration in minutes to human-readable format.

    Args:
        minutes (int): Duration in minutes

    Returns:
        str: Formatted duration string
    """
    if minutes < 60:
        return f"{minutes}min"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {remaining_minutes}min"


def get_seat_row_and_number(seat_number):
    """
    Extract row and number from a seat number.

    Args:
        seat_number (str): The seat number (e.g., 'A1')

    Returns:
        tuple: (row, number) or (None, None) if invalid
    """
    if not validate_seat_number_format(seat_number):
        return None, None

    normalized = normalize_seat_number(seat_number)
    row = normalized[0]
    number = int(normalized[1:])

    return row, number


def generate_seat_map(total_seats, booked_seats=None):
    """
    Generate a simple seat map representation.

    Args:
        total_seats (int): Total number of seats
        booked_seats (list): List of booked seat numbers

    Returns:
        dict: Seat map with availability information
    """
    if booked_seats is None:
        booked_seats = []

    # Simple seat map: assume 10 seats per row
    seats_per_row = 10
    rows_needed = (total_seats // seats_per_row) + (1 if total_seats % seats_per_row > 0 else 0)

    seat_map = {}
    seat_count = 0

    for row_idx in range(rows_needed):
        row_letter = chr(ord('A') + row_idx)
        row_seats = {}

        for seat_num in range(1, seats_per_row + 1):
            if seat_count >= total_seats:
                break

            seat_number = f"{row_letter}{seat_num}"
            row_seats[seat_number] = {
                'available': seat_number not in booked_seats,
                'seat_number': seat_number
            }
            seat_count += 1

        if row_seats:
            seat_map[row_letter] = row_seats

        if seat_count >= total_seats:
            break

    return seat_map


def calculate_booking_statistics(bookings_queryset):
    """
    Calculate statistics for a set of bookings.

    Args:
        bookings_queryset: Django QuerySet of bookings

    Returns:
        dict: Statistics including counts and percentages
    """
    total_bookings = bookings_queryset.count()

    if total_bookings == 0:
        return {
            'total_bookings': 0,
            'active_bookings': 0,
            'cancelled_bookings': 0,
            'cancellation_rate': 0.0
        }

    active_bookings = bookings_queryset.filter(status='booked').count()
    cancelled_bookings = bookings_queryset.filter(status='cancelled').count()

    return {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'cancelled_bookings': cancelled_bookings,
        'cancellation_rate': (cancelled_bookings / total_bookings) * 100 if total_bookings > 0 else 0
    }


def paginate_queryset(queryset, page_size=20, page_number=1):
    """
    Simple pagination utility.

    Args:
        queryset: Django QuerySet to paginate
        page_size (int): Number of items per page
        page_number (int): Page number (1-based)

    Returns:
        dict: Paginated results with metadata
    """
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(queryset, page_size)
    total_items = paginator.count
    total_pages = paginator.num_pages

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(total_pages)

    return {
        'items': list(page),
        'page_number': page.number,
        'page_size': page_size,
        'total_items': total_items,
        'total_pages': total_pages,
        'has_next': page.has_next(),
        'has_previous': page.has_previous()
    }


class ResponseHelper:
    """
    Helper class for standardizing API responses.
    """

    @staticmethod
    def success_response(data=None, message="Success", status_code=200):
        """
        Create a standardized success response.
        """
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return response

    @staticmethod
    def error_response(message="Error", details=None, status_code=400):
        """
        Create a standardized error response.
        """
        response = {
            'success': False,
            'error': message
        }
        if details is not None:
            response['details'] = details
        return response

    @staticmethod
    def paginated_response(items, pagination_info, message="Success"):
        """
        Create a standardized paginated response.
        """
        return {
            'success': True,
            'message': message,
            'data': items,
            'pagination': pagination_info
        }
