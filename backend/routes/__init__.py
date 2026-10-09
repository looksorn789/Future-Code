
from .auth import auth_bp

#Exportable routes for methods with one parameters which is the whole app itself
def register_routes(app): #We use blueprints to group related routes so they can be defined separetly from the main app
    app.register_blueprint(auth_bp) 