import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Flask Secret Key
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "capacity_connect_default_secret_change_me"
)

# PostgreSQL Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Flask Debug Mode
DEBUG = os.getenv("DEBUG", "True").lower() == "true"