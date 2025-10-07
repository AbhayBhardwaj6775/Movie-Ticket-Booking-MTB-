## Movie Ticket Booking (Django + DRF)

Minimal movie ticket booking API with JWT auth, SQLite, and OpenAPI docs.

### Quick start (Windows / PowerShell)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# (Optional) Seed demo data: movies, shows, and sample seats
python manage.py seed_data

# (Optional) Create an admin user for Django admin
python manage.py createsuperuser

# Start the dev server
python manage.py runserver
```

Once running:
- **API root**: http://127.0.0.1:8000/
- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **OpenAPI schema**: http://127.0.0.1:8000/schema/
- **Admin**: http://127.0.0.1:8000/admin/

### Authentication
- **Signup**: `POST /signup` body: `{ "username": "string", "password": "string" }`
- **Login**: `POST /login` → returns `access` and `refresh` JWTs
- **Authorization header**: `Authorization: Bearer <access-token>`

### Core endpoints
- `POST /signup`
- `POST /login`
- `GET /movies/` — list movies
- `GET /movies/<id>/shows/` — upcoming shows for a movie
- `POST /shows/<id>/book/` with body `{ "seat_number": "A1" }` — book a seat
- `POST /bookings/<id>/cancel/` — cancel a booking
- `GET /my-bookings/` — view current user bookings

### Project structure
```
booking/           # domain app: models, serializers, views, urls
core/              # project settings and root urls
templates/         # basic HTML templates (optional demo pages)
manage.py
requirements.txt
```

### Notes
- **Database**: SQLite by default; change in `core/settings.py` if needed.
- **JWT**: Provided by `djangorestframework-simplejwt`.
- **API docs**: Served by `drf-spectacular` at `/swagger/` and `/schema/`.
- **Tests**: run `python manage.py test`.
