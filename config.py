import os

SECRET_KEY = os.getenv("SECRET_KEY", "studentportal123")
DATABASE_URL = os.getenv("DATABASE_URL")

DEBUG = True