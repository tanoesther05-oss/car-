"""Configuration Django. Les secrets sont lus depuis l'environnement."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
    # vercel env pull writes this local-only file for production database tasks.
    load_dotenv(BASE_DIR / ".env.local", override=True)
except ImportError:
    pass

from django.core.exceptions import ImproperlyConfigured

ON_VERCEL = os.getenv("VERCEL", "").lower() == "1"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "" if ON_VERCEL else "dev-only-change-this-key")
if ON_VERCEL and not SECRET_KEY:
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY in Vercel project environment variables.")
DEBUG = os.getenv("DJANGO_DEBUG", "False" if ON_VERCEL else "True").lower() == "true"

allowed_hosts = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
csrf_origins = [o.strip().rstrip("/") for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
for vercel_host in (os.getenv("VERCEL_URL", ""), os.getenv("VERCEL_PROJECT_PRODUCTION_URL", "")):
    if vercel_host:
        host = vercel_host.removeprefix("https://").removeprefix("http://").rstrip("/")
        if host not in allowed_hosts:
            allowed_hosts.append(host)
        origin = f"https://{host}"
        if origin not in csrf_origins:
            csrf_origins.append(origin)
ALLOWED_HOSTS = allowed_hosts
CSRF_TRUSTED_ORIGINS = csrf_origins
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "students.apps.StudentsConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "emsp_car.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
              "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages", "students.context_processors.navigation"]}}]
WSGI_APPLICATION = "emsp_car.wsgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
database_url = os.getenv("DATABASE_URL", "")
if ON_VERCEL and not database_url:
    raise ImproperlyConfigured("Set DATABASE_URL to a persistent PostgreSQL database before deploying.")
if database_url.startswith(("postgres://", "postgresql://", "postgresql+")):
    import dj_database_url
    DATABASES["default"] = dj_database_url.parse(
        database_url,
        conn_max_age=0 if ON_VERCEL else 60,
        ssl_require=ON_VERCEL,
    )
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
