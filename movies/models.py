from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError


class Movie(models.Model):
    title = models.CharField(max_length=200, unique=True)
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(600)]
    )
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=100, blank=True)
    rating = models.CharField(max_length=10, blank=True)  # PG, PG-13, R, etc.
    release_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'

    def __str__(self):
        return f"{self.title} ({self.duration_minutes}min)"

    def clean(self):
        if self.duration_minutes and self.duration_minutes <= 0:
            raise ValidationError('Duration must be positive.')


class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='shows')
    screen_name = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    total_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(500)]
    )
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time']
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'
        unique_together = ['screen_name', 'date_time']

    def __str__(self):
        return f"{self.movie.title} - {self.screen_name} ({self.date_time.strftime('%Y-%m-%d %H:%M')})"

    def clean(self):
        if self.date_time and self.date_time <= timezone.now():
            raise ValidationError('Show time must be in the future.')
        if self.total_seats and self.total_seats <= 0:
            raise ValidationError('Total seats must be positive.')

    @property
    def available_seats(self):
        booked_count = self.bookings.filter(status='booked').count()
        return self.total_seats - booked_count

    @property
    def is_fully_booked(self):
        return self.available_seats <= 0

    def get_booked_seat_numbers(self):
        return list(
            self.bookings.filter(status='booked')
            .values_list('seat_number', flat=True)
        )


class Booking(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='bookings')
    seat_number = models.CharField(max_length=10)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    booking_reference = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        unique_together = ['show', 'seat_number', 'status']

    def __str__(self):
        return f"{self.user.username} - {self.show.movie.title} - {self.seat_number} ({self.status})"

    def clean(self):
        if self.show and self.seat_number:
            # Check for double booking
            existing_booking = Booking.objects.filter(
                show=self.show,
                seat_number=self.seat_number,
                status='booked'
            ).exclude(id=self.id).first()

            if existing_booking:
                raise ValidationError(f'Seat {self.seat_number} is already booked for this show.')

        # Validate seat number format (basic validation)
        if self.seat_number and not self.seat_number.strip():
            raise ValidationError('Seat number cannot be empty.')

    def save(self, *args, **kwargs):
        # Generate booking reference if not provided
        if not self.booking_reference:
            import uuid
            self.booking_reference = str(uuid.uuid4())[:8].upper()

        self.full_clean()
        super().save(*args, **kwargs)

    def cancel(self):
        """Cancel the booking"""
        if self.status == 'cancelled':
            raise ValidationError('Booking is already cancelled.')
        self.status = 'cancelled'
        self.save()

    @property
    def can_be_cancelled(self):
        """Check if booking can be cancelled (show hasn't started yet)"""
        return self.show.date_time > timezone.now() and self.status == 'booked'
