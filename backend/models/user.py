from extensions import db
from datetime import datetime, timezone

class User(db.Model): #create the user model to contain a primary key identifier, username/password/
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(15), unqie=True, nullable=False)
    password = db.Column()
    is_active = db.Column()
    created_at = db.Column()
    updated_at = db.Column()

