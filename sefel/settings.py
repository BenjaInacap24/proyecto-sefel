from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

import os
from urllib.parse import parse_qs, unquote, urlparse
from django.core.exceptions import ImproperlyConfigured

debug_default = 'false' if os.getenv('VERCEL') else 'true'
DEBUG = os.getenv('DJANGO_DEBUG', debug_default).strip().lower() in {'1', 'true', 'yes', 'on'}
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'local-prototype-only-change-before-deployment')
if not DEBUG and SECRET_KEY == 'local-prototype-only-change-before-deployment':
    raise ImproperlyConfigured('Set DJANGO_SECRET_KEY in the production environment.')

vercel_host = os.getenv('VERCEL_URL', '').strip()
vercel_project_host = os.getenv('VERCEL_PROJECT_PRODUCTION_URL', '').strip()
vercel_hosts = list(filter(None, [vercel_host, vercel_project_host]))
allowed_hosts_default = '127.0.0.1,localhost' if DEBUG else ','.join(vercel_hosts)
ALLOWED_HOSTS = [host.strip() for host in os.getenv('DJANGO_ALLOWED_HOSTS', allowed_hosts_default).split(',') if host.strip()]
csrf_origins_default = ','.join(f'https://{host}' for host in vercel_hosts) if not DEBUG else ''
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', csrf_origins_default).split(',') if origin.strip()]

INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','portal']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'sefel.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'sefel.wsgi.application'

database_url = os.getenv('DATABASE_URL', '').strip()
if database_url:
    parsed = urlparse(database_url)
    if parsed.scheme not in {'postgres', 'postgresql'}:
        raise ImproperlyConfigured('DATABASE_URL must use the postgres:// or postgresql:// scheme.')
    query = parse_qs(parsed.query)
    database_options = {'sslmode': query.get('sslmode', ['require'])[0]}
    database_name = unquote(parsed.path.lstrip('/'))
    if not database_name:
        raise ImproperlyConfigured('DATABASE_URL must include a database name.')
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': database_name,
        'USER': unquote(parsed.username or ''),
        'PASSWORD': unquote(parsed.password or ''),
        'HOST': parsed.hostname or '',
        'PORT': parsed.port or '5432',
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': False,
        'OPTIONS': database_options,
        # Supabase's transaction pooler is recommended for short-lived Vercel functions.
        'DISABLE_SERVER_SIDE_CURSORS': (parsed.port == 6543),
    }}
elif DEBUG:
    DATABASES = {'default': {'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
else:
    raise ImproperlyConfigured('DATABASE_URL is required when DJANGO_DEBUG is false.')

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR/'static']
STATIC_ROOT = BASE_DIR/'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = Path(os.getenv('MEDIA_ROOT', '/tmp/sefel-media' if os.getenv('VERCEL') else BASE_DIR/'media'))
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/interno/ingresar/'
LOGIN_REDIRECT_URL = '/interno/'
LOGOUT_REDIRECT_URL = '/'
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

