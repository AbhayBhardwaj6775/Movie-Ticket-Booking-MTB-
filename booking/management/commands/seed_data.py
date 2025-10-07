from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from booking.models import Movie, Show


class Command(BaseCommand):
    help = 'Seed admin user and sample Movie/Show data'

    def handle(self, *args, **options):
        User = get_user_model()

        if not User.objects.filter(username='admin').exists():
            u = User.objects.create(username='admin', is_staff=True, is_superuser=True)
            u.set_password('admin123')
            u.save()
            self.stdout.write(self.style.SUCCESS('Created superuser admin/admin123'))
        else:
            self.stdout.write('Superuser admin exists')

        if not Movie.objects.filter(title='Inception').exists():
            m = Movie.objects.create(title='Inception', duration_minutes=148)
            Show.objects.create(
                movie=m,
                screen_name='Screen 1',
                date_time=timezone.now() + timedelta(hours=2),
                total_seats=50,
            )
            self.stdout.write(self.style.SUCCESS('Seeded sample movie/show'))
        else:
            self.stdout.write('Sample movie already exists')




