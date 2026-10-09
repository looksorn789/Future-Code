from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

cors = CORS() #Initialize middleware
db = SQLAlchemy() #Initialize db using sqlalchemy
migrate = Migrate() #Use migrate to create and apply schema changes to avoid calling create_all()

def init_db(app):
    db.init_app(app)
    migrate.init_app(app,db)