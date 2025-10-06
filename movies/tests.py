from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta

from .models import Movie, Show, Booking


class MovieModelTestCase(TestCase):
    def test_create_movie(self):
        movie = Movie.objects.create(
            title="Test Movie",
            duration_minutes=120
        )
        self.assertEqual(str(movie), "Test Movie (120min)")

    def test_movie_validation(self):
        movie = Movie(title="Test Movie", duration_minutes=-10)
        with self.assertRaises(Exception):
            movie.full_clean()


class ShowModelTestCase(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration_minutes=120
        )

    def test_create_show(self):
        future_time = timezone.now() + timedelta(days=1)
        show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=future_time,
            total_seats=100
        )
        self.assertEqual(show.available_seats, 100)

    def test_show_available_seats(self):
        future_time = timezone.now() + timedelta(days=1)
        show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=future_time,
            total_seats=100
        )

        user = User.objects.create_user(username='testuser', password='testpass')
        Booking.objects.create(
            user=user,
            show=show,
            seat_number="A1",
            status='booked'
        )

        self.assertEqual(show.available_seats, 99)


class BookingModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration_minutes=120
        )
        future_time = timezone.now() + timedelta(days=1)
        self.show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=future_time,
            total_seats=100
        )

    def test_create_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number="A1"
        )
        self.assertEqual(booking.status, 'booked')
        self.assertTrue(booking.can_be_cancelled)

    def test_booking_validation(self):
        # Create first booking
        Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number="A1"
        )

        # Try to create duplicate booking
        booking2 = Booking(
            user=self.user,
            show=self.show,
            seat_number="A1"
        )
        with self.assertRaises(Exception):
            booking2.full_clean()


class MovieAPITestCase(APITestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration_minutes=120,
            is_active=True
        )
        self.movie_list_url = reverse('movie-list')

    def test_get_movie_list(self):
        response = self.client.get(self.movie_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['movies']), 1)

    def test_get_movie_shows(self):
        future_time = timezone.now() + timedelta(days=1)
        Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=future_time,
            total_seats=100
        )

        url = reverse('movie-shows', kwargs={'movie_id': self.movie.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['shows']), 1)


class BookingAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration_minutes=120,
            is_active=True
        )
        future_time = timezone.now() + timedelta(days=1)
        self.show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=future_time,
            total_seats=100
        )

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_book_seat(self):
        url = reverse('book-seat', kwargs={'show_id': self.show.id})
        data = {'seat_number': 'A1'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

    def test_book_seat_duplicate(self):
        # First booking
        Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number="A1"
        )

        # Try to book same seat
        url = reverse('book-seat', kwargs={'show_id': self.show.id})
        data = {'seat_number': 'A1'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number="A1"
        )

        url = reverse('cancel-booking', kwargs={'booking_id': booking.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')

    def test_get_my_bookings(self):
        Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number="A1"
        )

        url = reverse('my-bookings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['bookings']), 1)

    def test_book_seat_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        url = reverse('book-seat', kwargs={'show_id': self.show.id})
        data = {'seat_number': 'A1'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
