import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345@localhost:5432/airline_reviews'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
