from datetime import timedelta

from flask import Blueprint, request
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from init import db, bcrypt
from models.user import User, user_schema, users_schema, user_registration_schema
from controllers.auth_utils import authorise_as_admin

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route("/register", methods=["POST"]) # Register a new user
def auth_register():
    """
    Creates a new user account with details provided.

    Expects a JSON payload with the keys 'name', 'email', 'phone', and 'password'. 
    The 'password' is hashed before saving. If any of these keys are missing, 
    it will return a not nullable error.

    Returns:
        Tuple: A tuple containing the serialized user object and the HTTP status code 201, indicating successful creation.
        Errors for any invalid or empty data inputs

    Example JSON:
    {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "0412345678",
        "password": "password"
    }
    """
    # Extract request data, expecting JSON containing 'email', 'password', 'name', and 'phone'
    body_data = request.get_json()
    
    # Validate incoming JSON data against user registration schema
    # Checks for required fields, formatting, other validation rules applied
    try:
        validated_data = user_registration_schema.load(body_data)
    except ValidationError as err:
        return (err.messages), 400

    # Creates new user with validated data
    # Note: Password is hashed for security
    user = User(
        name=validated_data.get('name'),
        email=validated_data.get('email'),
        phone=validated_data.get('phone'),
        password=bcrypt.generate_password_hash(validated_data.get('password')).decode('utf-8')
    )  

    # Adds new user to session and commits to DB (saves new user)
    db.session.add(user)
    db.session.commit()
    
    # Serialises newly created user (excluding the password) and returns with a 201 Created status
    # Confirms to user account creation
    return user_schema.dump(user), 201
    
@auth_bp.route("/login", methods=["POST"]) # Login a registered user
def auth_login():
    """
    Authenticates a user based on email and password, generating a JWT token upon successful authentication.

    Expects a JSON payload containing 'email' and 'password' keys. It checks these credentials against the database,
    and if they match a user's credentials, it generates and returns a JWT token for the user along with their email
    and admin status. The token is valid for 1 day.

    Returns:
        A JSON object with the user's email, a JWT token, and the user's admin status if authentication is successful.
        If authentication fails, it returns an error message indicating invalid credentials.

    Example request payload:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    # Extract request data, expecting JSON containing 'email' and 'password'
    body_data = request.get_json()
    # Query the database for a user with the provided email
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    # Execute the query and fetch the first result (if any)
    user = db.session.scalar(stmt)
    
    # Check if a user was found and the password matches hashed password in database
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # Generate a JWT token for the authenticated user, setting the token's expiry to 1 day
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # Return specified fields in response
        return {"email": user.email, "token": token, "is_admin": user.is_admin}
    else:
        # If either no user found or password is incorrect, return an error
        return {"error": "Invalid email or password"}, 401

@auth_bp.route("/users", methods=["GET"]) # View all users (as an admin)
# Ensure the user is logged in and a valid JWT token is provided
@jwt_required()
# Ensure the user has admin privileges  
@authorise_as_admin 
def get_all_users():
    """
    Retrieves a list of all users from the database, restricted to admin only.
    
    Requires JWT authentication and admin status.
    
    Returns:
        - JSON list of all users with a 200 OK status, if the request is authorised.
        - A 403 Forbidden error if the requesting user is not an admin.
    """
    # Retrieve all users from the database
    users = db.session.query(User).all()
    
    # Serialise and return the list of users
    return users_schema.dump(users), 200

@auth_bp.route("/user/<int:user_id>", methods=["GET"]) # Account holder or admin can view single account/ their own account
@jwt_required()
def get_user(user_id):
    """
    Retrieves details of a specific user by user ID. Can be accessed by 
    the account holder or an admin. Other users are denied access.

    Requires JWT authentication. The JWT token must belong to an admin or the user 
    whose details are being requested.

    Returns:
        - JSON object containing the user's details with a 200 OK status, if access is granted.
        - A 403 error if the requesting user is neither the account holder nor an admin.
        - A 404 Not Found error if the user with the specified ID does not exist.
    """
    # Obtain ID of the current user from the JWT token
    current_user_id = int(get_jwt_identity())
    # Fetch the current user from database
    current_user = db.session.get(User, current_user_id)

    # Check if the current user is trying to access their own data or is an admin
    if current_user_id != user_id and not current_user.is_admin:
        # Access is denied if neither condition is met
        return {"error": "Access denied"}, 403

    # Retrieve the user object for the specified user_id
    user = db.session.get(User, user_id)
    if not user:
        # If no user is found with provided ID, return an error
        return {"error": "User not found"}, 404

    # Serialise and return the user object
    return user_schema.dump(user), 200

@auth_bp.route("/update", methods=["PUT"])  # Update user
@jwt_required()
def update_account():
    user_id = get_jwt_identity()
    body_data = request.get_json()

    user = db.session.get(User, user_id)
    if not user:
        return {"error": "User not found"}, 404

    user.name = body_data.get('name', user.name)
    user.email = body_data.get('email', user.email)
    user.phone = body_data.get('phone', user.phone)

    password = body_data.get('password')
    if password:
        user.password = bcrypt.generate_password_hash(password).decode('utf-8')

    db.session.commit()
    return user_schema.dump(user), 200

@auth_bp.route("/delete/<int:user_id>", methods=["DELETE"])  # Delete user
@jwt_required()
def delete_account(user_id):
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    if not current_user.is_admin and current_user_id != str(user_id):
        return {"error": "Unauthorised"}, 403

    user_to_delete = db.session.get(User, user_id)
    if not user_to_delete:
        return {"error": "User not found"}, 404

    db.session.delete(user_to_delete)
    db.session.commit()
    return {"message": "User deleted successfully"}, 200


