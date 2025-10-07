from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model


class Movie(models.Model):
    title = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.title


class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='shows')
    screen_name = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    total_seats = models.PositiveIntegerField()

    class Meta:
        ordering = ['date_time']

    def __str__(self) -> str:
        return f"{self.movie.title} @ {self.screen_name} {self.date_time}"


class Booking(models.Model):
    STATUS_BOOKED = 'booked'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_BOOKED, 'Booked'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='bookings')
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='bookings')
    seat_number = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['show', 'seat_number'],
                condition=Q(status='booked'),
                name='unique_booked_seat_per_show',
            )
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user} -> {self.show} seat {self.seat_number} ({self.status})"

# Create your models here.
