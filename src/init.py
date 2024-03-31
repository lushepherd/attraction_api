from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager


# Provides access to all the functions and classes from SQLAlchemy to interact with the database.
db = SQLAlchemy()

# Used for object serialisation and deserialisation
# (converting objects to and from JSON format), as well as for validating
# input data against a predefined schema.
ma = Marshmallow()

# Used for hashing passwords before they are stored in
# the database, and for verifying passwords at authentication.
bcrypt = Bcrypt()

# Manages the creation, sending, and validation of JSON Web Tokens (JWT) for
# secure authentication in the Flask application.
jwt = JWTManager()