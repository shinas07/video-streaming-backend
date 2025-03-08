# Video Streaming Backend

A Django-based backend for a video streaming application with OpenCV multi-threaded streaming and RESTful API endpoints.

## 🎯 Features

- **User Authentication**
  - Registration with email
  - JWT token-based authentication
  - User login/logout functionality

- **Video Management**
  - Upload and store video files
  - View, edit, and delete videos
  - Video searching by name
  - View count tracking

- **Streaming Capabilities**
  - Multi-threaded video streaming using OpenCV
  - Efficient stream management
  - Stream control (start/stop functionality)

## 🛠️ Tech Stack

- **Framework**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Video Processing**: OpenCV
- **Deployment**: Railway

## 📁 Project Structure

```
backend/
├── accounts/              # User authentication app
├── video_app/             # Video management app
├── video_streaming/       # Main project configuration
├── media/                 # User uploaded files
├── static/                # Static files
├── staticfiles/           # Collected static files
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables
├── manage.py              # Django management script
├── railway.sh             # Deployment script
└── Procfile               # Process file for deployment
```

## 🚀 Installation and Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Git

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/shinas07/video-streaming-backend.git
   cd video-streaming-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file with the following variables:
   ```
   DB_NAME=video_streaming_db
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   CORS_ALLOWED_ORIGINS=http://localhost:5173
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🔌 API Endpoints

### Authentication

- `POST /auth/register/` - Register a new user
- `POST /auth/login/` - Login user and get tokens
- `POST /auth/refresh/` - Refresh access token
- `POST /auth/logout/` - Logout user

### Videos

- `GET /api/videos/` - List all videos
- `POST /api/videos/` - Create a new video
- `GET /api/videos/<id>/` - Retrieve a specific video
- `PUT /api/videos/<id>/` - Update a specific video
- `DELETE /api/videos/<id>/` - Delete a specific video
- `GET /api/videos/search/` - Search videos by name
- `GET /api/videos/my_videos/` - List authenticated user's videos
- `POST /api/videos/<id>/increment_views/` - Increment video view count
- `GET /api/videos/<id>/stream/` - Stream a specific video
- `GET /api/videos/<id>/stop-stream/` - Stop streaming a video

## 🧪 Testing

Run the test suite using:

```bash
pytest
# or
python manage.py test
```

## 🚢 Deployment

The application is containerized and deployed on Railway.

## 🔒 Security Features

- JWT Authentication
- CSRF Protection
- Secure password hashing
- Protected API endpoints
