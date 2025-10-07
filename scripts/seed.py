import os
import django


def main() -> None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta
    from booking.models import Movie, Show

    User = get_user_model()

    if not User.objects.filter(username='admin').exists():
        u = User.objects.create(username='admin', is_staff=True, is_superuser=True)
        u.set_password('admin123')
        u.save()
        print('Created superuser admin/admin123')
    else:
        print('Superuser admin exists')

    if not Movie.objects.filter(title='Inception').exists():
        m = Movie.objects.create(title='Inception', duration_minutes=148)
        Show.objects.create(
            movie=m,
            screen_name='Screen 1',
            date_time=timezone.now() + timedelta(hours=2),
            total_seats=50,
        )
        print('Seeded sample movie/show')
    else:
        print('Sample movie already exists')


if __name__ == '__main__':
    main()




