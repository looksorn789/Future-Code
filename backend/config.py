import os
from dotenv import load_dotev

directory = os.path.dirname(os.path.abspath(__file__))

class Config:
    JWT_SECRET = os.environ[JWT_SECRET] #Fetch JWT SECRET from env file and store it for logged in users
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000") #Set current url to local host/testing environment
    ENV = os.getenv("ENV", "development") #Get env file
    DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(directory, "futurecode.db")) #Subject to change, defaulted for sqlite


