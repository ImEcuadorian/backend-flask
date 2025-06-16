import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'postgresql://myuser2:mypassword@db2:5432/mydatabase2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
