from django.contrib import admin
from .models import Movie, Show, Booking


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_minutes', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)
    list_editable = ('is_active',)


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('movie', 'screen_name', 'date_time', 'total_seats', 'booked_seats', 'available_seats')
    list_filter = ('screen_name', 'date_time', 'movie')
    search_fields = ('movie__title', 'screen_name')
    ordering = ('date_time',)
    readonly_fields = ('booked_seats', 'available_seats')

    def booked_seats(self, obj):
        return obj.bookings.filter(status='booked').count()
    booked_seats.short_description = 'Booked Seats'

    def available_seats(self, obj):
        return obj.total_seats - obj.bookings.filter(status='booked').count()
    available_seats.short_description = 'Available Seats'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'show', 'seat_number', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'show__screen_name')
    search_fields = ('user__username', 'show__movie__title', 'seat_number')
    ordering = ('-created_at',)
    list_editable = ('status',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'show', 'show__movie')
