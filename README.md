# GovDock - Government Document Management System

Django-based document management system for government documents with QR code integration.

## 🚀 Features

- Document upload and management
- QR code generation and verification
- User authentication and authorization
- ReCAPTCHA integration for security
- Responsive admin interface with Jazzmin
- Static file serving with WhiteNoise
- Docker support for easy deployment

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL (optional, SQLite by default)

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd GovDock
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py makeadmin
# Or manually: python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic --no-input
```

8. **Run development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Configure environment**
```bash
cp .env.example .env
# Edit .env with production settings
```

2. **Build and run containers**
```bash
docker-compose up -d --build
```

3. **Check logs**
```bash
docker-compose logs -f
```

4. **Stop containers**
```bash
docker-compose down
```

### Using Docker Only

1. **Build the image**
```bash
docker build -t govdock:latest .
```

2. **Run the container**
```bash
docker run -d \
  --name govdock \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/static:/app/static \
  govdock:latest
```

## 🔧 Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Database (Optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:password@host:port/database

# ReCAPTCHA
RECAPTCHA_PUBLIC_KEY=your-recaptcha-public-key
RECAPTCHA_PRIVATE_KEY=your-recaptcha-private-key

# Localization
LANGUAGE_CODE=uz-UZ
TIME_ZONE=Asia/Tashkent
```

### Generating Secret Key

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 📦 Project Structure

```
GovDock/
├── config/              # Django settings and configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docs/                # Main application
│   ├── management/
│   │   └── commands/
│   │       └── makeadmin.py
│   ├── models.py
│   ├── views.py
│   └── ...
├── templates/           # HTML templates
├── static/             # Static files (CSS, JS, images)
├── media/              # User uploaded files
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── entrypoint.sh       # Container entrypoint script
├── requirements.txt    # Python dependencies
├── manage.py          # Django management script
└── .env               # Environment variables (not in git)
```

## 🚀 Production Deployment

### Railway / Render / Heroku

1. **Set environment variables** in your platform's dashboard
2. **Connect your repository**
3. **Set build command:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set start command:**
   ```bash
   ./entrypoint.sh
   ```

### VPS / Cloud Server

1. **Install Docker and Docker Compose**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

2. **Clone repository**
```bash
git clone <repository-url>
cd GovDock
```

3. **Configure environment**
```bash
nano .env
# Add your production settings
```

4. **Deploy with Docker Compose**
```bash
docker-compose up -d --build
```

5. **Setup Nginx reverse proxy** (optional)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/GovDock/static/;
    }

    location /media/ {
        alias /path/to/GovDock/media/;
    }
}
```

6. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 🔑 Management Commands

### Create Admin User
```bash
python manage.py makeadmin
```

### Collect Static Files
```bash
python manage.py collectstatic --no-input
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Clear Database
```bash
python manage.py flush
```

## 🐛 Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic --clear --no-input
```

### Database migration issues
```bash
python manage.py migrate --run-syncdb
```

### Permission denied for entrypoint.sh
```bash
chmod +x entrypoint.sh
```

### Docker container exits immediately
```bash
docker-compose logs web
```

## 📝 License

[Add your license here]

## 👥 Contributors

[Add contributors here]

## 📧 Contact

For issues and questions, please open an issue on GitHub.

---

**Note:** Always use strong secret keys and never commit sensitive information to version control.