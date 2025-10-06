#!/usr/bin/env python
"""
Script to set up demo data for the Movie Booking System.
Run this after running migrations to populate the database with sample data.

Usage:
    python setup_demo_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_booking_system.settings')
django.setup()

from django.contrib.auth.models import User
from movies.models import Movie, Show


def create_demo_data():
    """Create demo data for testing the application."""

    print("Setting up demo data...")

    # Create demo users
    if not User.objects.filter(username='demo').exists():
        demo_user = User.objects.create_user(
            username='demo',
            email='demo@example.com',
            password='demopass123',
            first_name='Demo',
            last_name='User'
        )
        print(f"Created demo user: {demo_user.username}")

    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print(f"Created admin user: {admin_user.username}")

    # Create demo movies
    movies_data = [
        {
            'title': 'The Avengers: Endgame',
            'duration_minutes': 181,
            'description': 'The epic conclusion to the Infinity Saga.',
            'genre': 'Action, Adventure, Drama',
            'rating': 'PG-13'
        },
        {
            'title': 'Spider-Man: No Way Home',
            'duration_minutes': 148,
            'description': 'Spider-Man faces his greatest challenge yet.',
            'genre': 'Action, Adventure, Sci-Fi',
            'rating': 'PG-13'
        },
        {
            'title': 'The Dark Knight',
            'duration_minutes': 152,
            'description': 'Batman faces the Joker in Gotham City.',
            'genre': 'Action, Crime, Drama',
            'rating': 'PG-13'
        },
        {
            'title': 'Inception',
            'duration_minutes': 148,
            'description': 'A thief who steals corporate secrets through dream-sharing technology.',
            'genre': 'Action, Sci-Fi, Thriller',
            'rating': 'PG-13'
        },
        {
            'title': 'Interstellar',
            'duration_minutes': 169,
            'description': 'A team of explorers travel through a wormhole in space.',
            'genre': 'Adventure, Drama, Sci-Fi',
            'rating': 'PG-13'
        }
    ]

    created_movies = []
    for movie_data in movies_data:
        movie, created = Movie.objects.get_or_create(
            title=movie_data['title'],
            defaults=movie_data
        )
        if created:
            print(f"Created movie: {movie.title}")
        created_movies.append(movie)

    # Create demo shows
    screens = ['Screen A', 'Screen B', 'Screen C', 'IMAX Screen']
    base_time = timezone.now() + timedelta(hours=2)  # Start 2 hours from now

    for i, movie in enumerate(created_movies):
        # Create multiple shows for each movie
        for j in range(3):  # 3 shows per movie
            show_time = base_time + timedelta(days=j, hours=i*2)
            screen = screens[j % len(screens)]

            show, created = Show.objects.get_or_create(
                movie=movie,
                screen_name=screen,
                date_time=show_time,
                defaults={
                    'total_seats': 100,
                    'price': 12.50 + (j * 2.50)  # Varying prices
                }
            )
            if created:
                print(f"Created show: {movie.title} at {screen} on {show_time.strftime('%Y-%m-%d %H:%M')}")

    print("Demo data setup completed!")
    print("\nYou can now:")
    print("1. Login with demo user - username: 'demo', password: 'demopass123'")
    print("2. Login as admin - username: 'admin', password: 'admin123'")
    print("3. Visit /admin/ for Django admin interface")
    print("4. Visit /swagger/ for API documentation")


if __name__ == '__main__':
    create_demo_data()
