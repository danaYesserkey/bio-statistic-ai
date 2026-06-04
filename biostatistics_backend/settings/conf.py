from decouple import config
from datetime import timedelta  # noqa
from pathlib import Path  # noqa
from dotenv import load_dotenv

load_dotenv()

# Environment
ENV_OPTIONS = ("local", "prod")

ENV_ID = config("ENVIRONMENT", default="local")

SECRET_KEY = config("DJANGO_SECRET_KEY")


try:
    settings_env_module = f"settings.env.{ENV_ID}"

    globals().update(__import__(settings_env_module, fromlist=["*"]).__dict__)
except ImportError as e:
    raise ImportError(f"Could not import settings for environment '{ENV_ID}': {e}")


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
