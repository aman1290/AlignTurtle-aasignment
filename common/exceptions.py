"""
Custom exceptions for the Movie Booking System.
"""


class BookingError(Exception):
    """
    Custom exception for booking-related errors.
    """
    def __init__(self, message="Booking operation failed"):
        self.message = message
        super().__init__(self.message)


class SeatNotAvailableError(BookingError):
    """
    Exception raised when trying to book an unavailable seat.
    """
    def __init__(self, seat_number):
        message = f"Seat {seat_number} is not available"
        super().__init__(message)


class ShowFullyBookedError(BookingError):
    """
    Exception raised when trying to book a seat in a fully booked show.
    """
    def __init__(self):
        message = "This show is fully booked"
        super().__init__(message)


class InvalidSeatNumberError(BookingError):
    """
    Exception raised when an invalid seat number is provided.
    """
    def __init__(self, seat_number):
        message = f"Invalid seat number: {seat_number}"
        super().__init__(message)


class BookingNotFoundError(Exception):
    """
    Exception raised when a booking is not found.
    """
    def __init__(self, booking_id):
        message = f"Booking with ID {booking_id} not found"
        super().__init__(message)


class UnauthorizedBookingActionError(Exception):
    """
    Exception raised when a user tries to perform an unauthorized action on a booking.
    """
    def __init__(self, action="access"):
        message = f"Unauthorized to {action} this booking"
        super().__init__(message)


class ShowNotFoundError(Exception):
    """
    Exception raised when a show is not found.
    """
    def __init__(self, show_id):
        message = f"Show with ID {show_id} not found"
        super().__init__(message)


class PastShowBookingError(BookingError):
    """
    Exception raised when trying to book a seat for a past show.
    """
    def __init__(self):
        message = "Cannot book seats for past shows"
        super().__init__(message)
