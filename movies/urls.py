from django.urls import path
from . import views

urlpatterns = [
    # Movie endpoints
    path('movies/', views.movie_list, name='movie-list'),
    path('movies/<int:movie_id>/shows/', views.movie_shows, name='movie-shows'),

    # Show endpoints
    path('shows/<int:show_id>/', views.show_detail, name='show-detail'),
    path('shows/<int:show_id>/book/', views.book_seat, name='book-seat'),
    path('shows/', views.upcoming_shows, name='upcoming-shows'),

    # Booking endpoints
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('my-bookings/', views.my_bookings, name='my-bookings'),
]
