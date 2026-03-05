from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'dev-key-cyberum-kids'
DEBUG = True
ALLOWED_HOSTS = ["detatensipkuk.beget.app", "46.173.28.207", "127.0.0.1", "localhost", "platform.cyberumschool.ru", "www.platform.cyberumschool.ru"]

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'courses',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'cyberumkids.urls'
TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[], 'APP_DIRS':True,
    'OPTIONS':{'context_processors':[
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]}
}]
WSGI_APPLICATION = 'cyberumkids.wsgi.application'
DATABASES = {'default':{'ENGINE':'django.db.backends.sqlite3','NAME': BASE_DIR/'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE='ru'; TIME_ZONE='Europe/Moscow'; USE_I18N=True; USE_TZ=True
STATIC_URL='/static/'; STATICFILES_DIRS=[BASE_DIR/'static']
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CSRF_TRUSTED_ORIGINS = [
    "http://detatensipkuk.beget.app",
    "https://detatensipkuk.beget.app",
]