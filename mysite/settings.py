import os
import environ

from pathlib import Path
from datetime import timedelta
from decouple import config
from dj_database_url import parse as dburl

# プロジェクトのルートディレクトリを取得(現在の__file__objectの親の親を参照)
BASE_DIR = Path(__file__).resolve().parent.parent

# envファイルを読み込む
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

#本番環境では、ALLOWED_HOSTSを指定する
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "accounts",
    'tickets',
    "cloudinary",
    "cloudinary_storage",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'mysite.middlewares.SameSiteMiddleware',
]


#本番環境では、CORS_ORIGIN_WHITELISTを指定する
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "http://localhost:3000",
    "https://127.0.0.1:3000",
    "https://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://ec2-18-205-158-217.compute-1.amazonaws.com"
]


ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1', 'https://ec2-18-205-158-217.compute-1.amazonaws.com']
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True

default_dburl = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')

#本番環境では、DATABASE＿URLにPostgreSQLのURLを指定する
if os.getenv('DJANGO_ENV') == 'production':  # 本番環境の場合
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL')
        )
    }
else:  # 開発環境の場合
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / "db.sqlite3",
        }
    }
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
#静的ファイルの設定
STATIC_ROOT = str(BASE_DIR / 'staticfiles')

#メディアルートの設定
MEDIA_URL = '/media/'

#Cloudinaryの設定
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}

#メール設定
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

#Rest Frameworkの設定
REST_FRAMEWORK = {
    #認証が必要
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    #JWT認証
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    #日付
    'DATETIME_FORMAT': "%Y/%m/%d %H:%M",
}

#JWTの設定
SIMPLE_JWT = {
    #アクセストークン(1日)
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    #リフレッシュトークン(5日)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=5),
    #認証タイプ
    "AUTH_HEADER_TYPES": ("JWT",),
    #認証トークン
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# Djoserの設定(Django用の認証ライブラリ)
DJOSER = {
    #メールアドレスでログイン
    'LOGIN_FIELD': 'email',
    #アカウント本登録メール
    "SEND_ACTIVATION_EMAIL": True,
    #アカウント本登録完了メール
    "SEND_CONFIRMATION_EMAIL": True,
    #メールアドレスの変更完了メール
    "USERNAME_CHANGED_EMAIL_CONFIRMATION": True,
    #パスワード変更完了メール
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    #アカウント登録時に確認用パスワード必須
    "USER_CREATE_PASSWORD_RETYPE": True,
    #メールアドレス変更時に確認用メールアドレス必須
    "SET_USERNAME_RETYPE": True,
    #パスワード変更時に確認用パスワード必須
    "SET_PASSWORD_RETYPE": True,
    #アカウント本登録用URL
    "ACTIVATION_URL": "signup/{uid}/{token}",
    #パスワードリセット完了用URL
    "PASSWORD_RESET_CONFIRM_URL": "reset-password/{uid}/{token}",
    #カスタムユーザー用シリアライザ
    "SERIALIZERS": {
        "user_create": "accounts.serializers.UserSerializer",
        "user": "accounts.serializers.UserSerializer",
        "current_user": "accounts.serializers.UserSerializer",
    },
    "EMAIL": {
        #アカウント本登録
        "activation": "accounts.email.ActivationEmail",
        #アカウント本登録完了
        "confirmation": "accounts.email.ConfirmationEmail",
        #パスワード再設定
        "password_reset": "accounts.email.ForgotPasswordEmail",
        #パスワード再設定完了
        "password_changed_confirmation": "accounts.email.ResetPasswordEmail",
    },
}

#ユーザーモデル
AUTH_USER_MODEL = "accounts.UserAccount"

#サイト設定
SITE_DOMAIN = env('SITE_DOMAIN')
SITE_NAME = env('SITE_NAME')

CACHES = {
    'default': {
        'BACKEND' : 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION' : 'unique-snowflake'
    }
}