import functools
from flask import g, abort
from flask_jwt_extended import get_jwt_identity

from models.user import User
from init import db, bcrypt

def authorise_as_admin(fn):
    """
    Decorator that enforces admin-only access to endpoints.
    
    Checks if the currently authenticated user is an admin. 
    If not, it returns a 403 Forbidden error, indicating that the operation 
    requires admin privileges.
    
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        stmt = db.select(User).filter_by(id=user_id)
        user = db.session.scalar(stmt)
        if user.is_admin:
            return fn(*args, **kwargs)
        else:
            return {"error": "Not authorised. Admin access required."}, 403
        
    return wrapper

def load_current_user(fn):
    """
    Decorator that loads the current user from the database and attaches it to Flask's `g` context.
    
    Before invoking the decorated endpoint, this decorator fetches the currently authenticated 
    user based on the JWT token's identity. If no user is found, it aborts the request with a 
    404 Not Found error.
    
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        
        if not user:
            abort(404)
        
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper

def hash_password(password):
    """
    Hashes a plaintext password using Bcrypt.
    """
    return bcrypt.generate_password_hash(password).decode('utf-8')

def validate_data(schema, data, partial=False):
    """
    Validate data against a schema.

    This function attempts to validate the data against the provided Marshmallow schema. It supports
    partial validation, useful for update operations where not all fields may be provided.
    """
    return schema.load(data, partial=partial)