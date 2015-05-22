"""
Django settings for myjango project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i6-mt6p=#w=iy2^@u0z88l_g-(fx_oq6x-waj_&&+*(re5gn_3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',  
    'django.contrib.contenttypes',  
    'django.contrib.sessions',  
   # 'django.contrib.sites',  
   
    'django.contrib.messages',  
    'django.contrib.staticfiles',  
    'django.contrib.admin', 
    'django.contrib.admindocs',  
    'alert',
    'pagination',
    'app',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS=(
    'django.contrib.auth.context_processors.auth',
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request")

ROOT_URLCONF = 'myjango.urls'
WSGI_APPLICATION = 'myjango.wsgi.application'
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.mysql', 
         'NAME': 'alert',    
         'USER': 'root',   
         'PASSWORD': '1234',
         'HOST': '', 
         'PORT': '3306', 
    },
             
        'other': {
         'ENGINE': 'django.db.backends.mysql', 
         'NAME': 'test',    
         'USER': 'root',   
         'PASSWORD': '1234',
         'HOST': '', 
         'PORT': '3306', 
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = ''
STATIC_URL = '/static/'

LOGIN_URL = '/accounts/login'

LOGIN_REDIRECT_URL = '/alert'
