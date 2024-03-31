import os

from flask import Flask
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from marshmallow.exceptions import ValidationError

from init import db, ma, bcrypt, jwt

def create_app():
    """
    Initialises and configures the Flask application, database, and extensions.
    
    Sets up error handlers for common HTTP status codes and database integrity errors.
    Registers blueprints for different parts of the application to organize routes.
    """
    app = Flask(__name__)
    app.json.sort_keys = False

    # Configures the app from environment variables (in the .env file)
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATABASE_URI")
    app.config["JWT_SECRET_KEY"]=os.environ.get("JWT_SECRET_KEY")
    
    # Initialises extensions in app
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Global error handlers for common errors that return JSON responses
    @app.errorhandler(404)
    def not_found(err):
        return {"error": str(err)}, 404
        
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return {"error": error.messages}, 400
    
    @app.errorhandler(400)
    def bad_request(err):
        return ({"error": str(err)}), 400
    
    @app.errorhandler(401)
    def unauthorised_error(err):
        return ({"error": str(err)}), 401
    
    @app.errorhandler(403)
    def forbidden(err):
        return {"error": str(err)}, 403

    @app.errorhandler(500)
    def internal_server_error(err):
        return {"error": str(err)}, 500
    
    @app.errorhandler(500)
    def internal_server_error(err):
        return {"error": str(err)}, 500
    
    @app.errorhandler(IntegrityError)
    def integrity_error(err):
        """
        Custom handler for database integrity errors, including not null violations and unique constraint violations.
        Returns some specific errors for unique violations.
        """
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400

        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            constraint_name = err.orig.diag.constraint_name
            if constraint_name == 'uix_email':
                error_message = "Email address already in use"
            elif constraint_name == 'uix_phone':
                error_message = "Phone number already in use"
            elif constraint_name == 'attractions_name_key':
                error_message = "An attraction with this name already exists."
            else:
                error_message = "A unique constraint violation occurred."
            return {"error": error_message}, 409

        return {"error": "A database integrity error occurred."}, 500
        
    from controllers.cli_controller import db_commands
    app.register_blueprint(db_commands)
    
    from controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)
    
    from controllers.booking_controller import booking_bp
    app.register_blueprint(booking_bp)
    
    from controllers.attraction_controller import attraction_bp
    app.register_blueprint(attraction_bp)
    
    from controllers.review_controller import review_bp
    app.register_blueprint(review_bp)
    
    return app