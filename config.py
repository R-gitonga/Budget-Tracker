import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent

# Load variables from <project root>/.env (real environment variables win over the file).
load_dotenv(BASE_DIR / ".env")


def _require(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required setting '{name}'. "
            f"Copy .env.example to .env and fill it in."
        )
    return value


def _database_uri():
    """Use DATABASE_URL if set (e.g. on Render/Heroku); otherwise build it from DB_* parts."""
    url = os.environ.get("DATABASE_URL")
    if url:
        # Hosts may hand out 'postgres://' or plain 'postgresql://'. Newer SQLAlchemy
        # treats plain 'postgresql://' as the psycopg v3 driver, but requirements.txt
        # installs psycopg2, so name that driver explicitly.
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg2://" + url[len(prefix):]
        return url

    # URL.create() escapes special characters (@, :, /, #...) in the password for us.
    return URL.create(
        drivername="postgresql+psycopg2",
        username=_require("DB_USER"),
        password=_require("DB_PASSWORD"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        database=_require("DB_NAME"),
    )


class Config:
    SECRET_KEY = _require("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False