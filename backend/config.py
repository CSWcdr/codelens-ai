import os

from pathlib import Path
from typing import List

from dotenv import load_dotenv


BASE_DIR = Path(
    __file__
).resolve().parent


load_dotenv(
    BASE_DIR / ".env"
)


def get_bool_env(
    key: str,
    default: bool = False,
) -> bool:
    value = os.getenv(
        key
    )

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_list_env(
    key: str,
    default: List[str],
) -> List[str]:
    value = os.getenv(
        key
    )

    if not value:
        return default

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


APP_NAME = os.getenv(
    "APP_NAME",
    "CodeLens AI API",
)


APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
)


ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development",
).strip().lower()


DEBUG = get_bool_env(
    "DEBUG",
    ENVIRONMENT == "development",
)


DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


CORS_ORIGINS = get_list_env(
    "CORS_ORIGINS",
    DEFAULT_CORS_ORIGINS,
)


GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN"
)


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)