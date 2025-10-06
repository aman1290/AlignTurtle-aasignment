# Movie Booking System API

A Django REST Framework based movie ticket booking system with JWT authentication and Swagger documentation.

## Features

- User authentication (signup/login) with JWT
- Movie and show management
- Seat booking system with business logic
- Booking cancellation
- Comprehensive API documentation with Swagger
- Error handling and validation

## Tech Stack

- Python 3.8+
- Django 4.2
- Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- Swagger Documentation (drf-yasg)
- SQLite (default) / PostgreSQL

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aman1290/AlignTurtle-aasignment.git
   cd AlignTurtle-aasignment.git
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations movies users
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`

## API Documentation

### Swagger Documentation
Visit `http://127.0.0.1:8000/swagger/` for interactive API documentation.

### Authentication

#### Register a new user
```http
POST /api/signup/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}
```

#### Login and get JWT token
```http
POST /api/login/
Content-Type: application/json

{
    "username": "testuser",
    "password": "testpassword123"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using JWT Token

For all protected endpoints, include the JWT token in the Authorization header:
```http
Authorization: Bearer <your_access_token>
```

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/signup/` | Register a new user | No |
| POST | `/api/login/` | Login and get JWT token | No |
| GET | `/api/movies/` | List all movies | No |
| GET | `/api/movies/<id>/shows/` | List shows for a movie | No |
| POST | `/api/shows/<id>/book/` | Book a seat | Yes |
| POST | `/api/bookings/<id>/cancel/` | Cancel a booking | Yes |
| GET | `/api/my-bookings/` | List user's bookings | Yes |

### Example API Calls

#### List Movies
```http
GET /api/movies/
```

#### Book a Seat
```http
POST /api/shows/1/book/
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "seat_number": "A1"
}
```

#### Cancel Booking
```http
POST /api/bookings/1/cancel/
Authorization: Bearer <your_token>
```

## Project Structure

```
movie_booking_system/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── movie_booking_system/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── movies/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py
│   └── ...
│
└── common/
    ├── exceptions.py
    └── utils.py
```

## Business Rules

- **No double booking**: A seat cannot be booked twice for the same show
- **No overbooking**: Total bookings cannot exceed show capacity
- **Cancellation**: Users can only cancel their own bookings
- **Authentication**: All booking operations require valid JWT token

## Testing

Run tests with:
```bash
python manage.py test
```

## License

This project is for educational/internship purposes.
