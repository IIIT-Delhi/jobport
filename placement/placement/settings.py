import os
PROJECT_ROOT = os.path.abspath(
	os.path.join(os.path.dirname(__file__), ".."),
)

SECRET_KEY = '$8gtwkoh^#$x%a4=s)j5mn2a6x5s7%yzj&@dq$%46*u^s(yc6^'
DEBUG = True
TEMPLATE_DEBUG = True
# ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
	'suit',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'social.apps.django_app.default',
	'django.contrib.humanize',
	'jobport',
	'south',
	'bootstrap3',
	'timezone_field',
	'datetimezone_field',
	'bootstrap3_datetime',
	'googlecharts',
	'haystack',
	'djrill',
	'longerusernameandemail',
)

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
	'jobport.middleware.MyMiddleware',
)

ROOT_URLCONF = 'placement.urls'
WSGI_APPLICATION = 'placement.wsgi.application'

# DATABASES = {
# 	'default': {
# 			'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
# 			'NAME': 'jobport',                      # Or path to database file if using sqlite3.
# 			'USER': 'admin',
# 			'PASSWORD': 'placement@iiitd',
# 			'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
# 			'PORT': '',                      # Set to empty string for default.
# 		}
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_ROOT + '/jobport.db',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = ['iiitd.ac.in']
SOCIAL_AUTH_GOOGLE_OAUTH2_USE_DEPRECATED_API = True
SOCIAL_AUTH_GOOGLE_PLUS_USE_DEPRECATED_API = True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
#SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = False
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/newuser/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/needlogin/'
LOGIN_URL = '/needlogin/'

AUTHENTICATION_BACKENDS = (
	'social.backends.google.GoogleOAuth2',
	'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.core.context_processors.tz",
	"django.contrib.messages.context_processors.messages",
	'social.apps.django_app.context_processors.backends',
	'social.apps.django_app.context_processors.login_redirect',
	'django.core.context_processors.request',
	)

MEDIA_ROOT = 'files'
MEDIA_URL = '/files/'

MANDRILL_API_KEY = os.environ.get('MANDRILL_API_KEY')
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
EMAIL_HOST_USER = ''

GOOGLECHARTS_API = '1.1'

HAYSTACK_CONNECTIONS = {
	'default': {
		'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
		'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
	},
}
