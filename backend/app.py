from flask import Flask
from config import Config
from extensions import cors, init_db
from routes import register_routes

# Exportable Flask App with initialized middleware to connect between routes, db, and env variables
def create_app(config_class=Config): #Make flask app importable/accessable to other routes
    app = Flask(__name__) #Initialize flask framework
    app.config.from_object(config_class) #Initialize config variables
    cors.init_app(app, resources={r"api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}},
                  support_credentials=True) #Initialize api routing through middleware CORS
    init_db(app) #Initialize DB and SQL
    register_routes(app) #Initialize blueprints to define routes 
    return app 

