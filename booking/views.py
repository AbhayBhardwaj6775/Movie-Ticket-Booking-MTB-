from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Movie, Show, Booking
from .serializers import (
    SignupSerializer,
    MovieSerializer,
    ShowSerializer,
    BookingSerializer,
    BookSeatSerializer,
)

from django.views.generic import TemplateView


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]


class MovieShowsListView(generics.ListAPIView):
    serializer_class = ShowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Show.objects.filter(movie_id=self.kwargs['movie_id'])


class BookSeatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, show_id: int):
        show = Show.objects.select_for_update().get(id=show_id)
        serializer = BookSeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seat_number = serializer.validated_data['seat_number']

        # Validate seat range
        if seat_number < 1 or seat_number > show.total_seats:
            return Response({'detail': 'Seat number out of range.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lock current active bookings to avoid race on capacity calculations
        active_qs = Booking.objects.select_for_update().filter(show=show, status=Booking.STATUS_BOOKED)
        # Double-booking check
        if active_qs.filter(seat_number=seat_number).exists():
            return Response({'detail': 'Seat already booked.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check capacity (count of active bookings) after acquiring locks
        active_count = active_qs.count()
        if active_count >= show.total_seats:
            return Response({'detail': 'Show is fully booked.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.create(
                user=request.user,
                show=show,
                seat_number=seat_number,
                status=Booking.STATUS_BOOKED,
            )
        except IntegrityError:
            # Covers rare race where seat became booked between check and create
            return Response({'detail': 'Seat already booked.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class CancelBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, booking_id: int):
        try:
            booking = Booking.objects.select_for_update().get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        if booking.status == Booking.STATUS_CANCELLED:
            return Response({'detail': 'Booking already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=['status'])
        return Response({'detail': 'Booking cancelled.'}, status=status.HTTP_200_OK)


class MyBookingsListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


# ---------- HTML pages (BookMyShow-like simple UI) ----------

class AppHomePage(TemplateView):
    template_name = 'app/home.html'


class AppMovieDetailPage(TemplateView):
    template_name = 'app/movie_detail.html'


class AppMyBookingsPage(TemplateView):
    template_name = 'app/my_bookings.html'
