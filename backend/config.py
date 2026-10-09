import os
from pathlib import Path
from dotenv import load_dotenv

directory = Path(__file__).resolve().parent
load_dotenv(directory / ".env")

class Config:
    JWT_SECRET = os.environ["JWT_SECRET"] #Fetch JWT SECRET from env file and store it for logged in users
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000") #Set current url to local host/testing environment
    ENV = os.getenv("ENV", "development") #Get env file
    DATABASE_PATH = os.path.abspath(os.getenv("DATABASE_PATH", str(directory / "futurecode.db")))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH.replace(os.sep, '/')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

