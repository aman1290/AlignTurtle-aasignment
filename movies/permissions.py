from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a booking to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the booking.
        return obj.user == request.user


class IsBookingOwner(permissions.BasePermission):
    """
    Custom permission to only allow booking owners to cancel their bookings.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is the owner of the booking
        return obj.user == request.user


class CanBookSeat(permissions.BasePermission):
    """
    Custom permission to check if user can book a seat.
    """

    def has_permission(self, request, view):
        # Only authenticated users can book seats
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Additional checks can be added here if needed
        return True


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff to write, but allow read-only for others.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
