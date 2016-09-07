"""
Django settings for shopelectro project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from datetime import datetime
import dj_database_url


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gl9syc68r%rmb*1&yzz(4%cotfpb$dy&wkb_y5_d0*be0pfulq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# setting from docker example: https://github.com/satyrius/paid/
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',')]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'mptt',
    'widget_tweaks',
    'pages',
    'catalog',
    'ecommerce',
    'shopelectro',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
]

ROOT_URLCONF = 'shopelectro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ecommerce.context_processors.cart',
                'shopelectro.context_processors.shop'
            ],
        },
    },
]

WSGI_APPLICATION = 'shopelectro.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LOCALE_NAME = 'en_US'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'front/build'),
    ASSETS_DIR,
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DATABASE_URL = 'postgres://postgres:11@db/shopelectro'

DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        default=DATABASE_URL
    )
}

PRODUCTS_TO_LOAD = 30

SITE_CREATED = datetime(2013, 1, 1)

LOCALHOST = 'http://127.0.0.1:8000/'
BASE_URL = 'https://www.shopelectro.ru'

IMAGES = {
    'large': 'main',
    'small': 'small',
    'thumbnail': 'logo.svg'
}

# Autocomplete and search settings
SEARCH_SEE_ALL_LABEL = 'Смотреть все результаты'

# For sitemaps and sites framework
SITE_ID = 1
SITE_DOMAIN_NAME = 'www.shopelectro.ru'

# Used for order's email in ecommerce app
FAKE_ORDER_NUMBER = 4500

# Used to retrieve instances in ecommerce.Cart
PRODUCT_MODEL = 'shopelectro.Product'
CART_ID = 'cart'

# Used to define choices attr in definition of Order.payment_option field
# TODO uncomment in dev-796, first needed test yandex_kassa
PAYMENT_OPTIONS = (('cash', 'Наличные'),
                   ('cashless', 'Безналичные и денежные переводы'),)
                   # ('AC', 'Банковская карта'),
                   # ('PC', 'Яндекс.Деньги'),
                   # ('GP', 'Связной (терминал)'),
                   # ('AB', 'Альфа-Клик'),
                   # ('MC', 'Мобильный телефон'))

# Subjects for different types of emails sent from SE.
EMAIL_SUBJECTS = {
    'call': 'Обратный звонок',
    'order': 'Заказ №{0.id}',
    'yandex_order': 'Заказ №{0.id} | Яндекс.Касса',
    'one_click': 'Заказ в один клик №{}',
    'ya_feedback_request': 'Оцените нас на Яндекс.Маркете',
}

# Used in admin image uploads
MODEL_TYPES = {
    'Product': {
        'app_name': 'shopelectro',
        'dir_name': 'products',
    },
    'Category': {
        'app_name': 'shopelectro',
        'dir_name': 'categories',
    }
}

# Used mostly in breadcrumbs to generate URL for catalog's root.
CATEGORY_TREE_URL = 'category_tree'

# This need for using {% debug %} variable in templates.
INTERNAL_IPS = (
    '127.0.0.1',
)

# Some defaults for autocreation struct pages: index, catalog tree
# Pages with this data are created in DB only once.
PAGES = {
    'index': {
        'slug': 'index',
        'route': 'index',
        'title': 'Shopelectro | Элементы питания',
        'h1': 'Элементы питания в СПб с доставкой по России',
        'menu_title': 'Главная',
        'date_published': SITE_CREATED,
    },
    'category_tree': {
        'slug': 'category_tree',
        'route': 'category_tree',
        'title': 'Каталог товаров',
        'menu_title': 'Каталог',
        'date_published': SITE_CREATED,
    },
    'search': {
        'slug': 'search',
        'title': 'Результаты поиска',
        'date_published': SITE_CREATED,
    },
}
