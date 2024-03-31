from datetime import timedelta

from flask import Blueprint, request, abort, g
from flask_jwt_extended import create_access_token, jwt_required

from init import db, bcrypt
from models.user import User, UserSchema, user_schema, users_schema, user_registration_schema
from utils.auth_utils import authorise_as_admin, hash_password, validate_data, load_current_user

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
    
    Validation rules: 
    - name: Must contain only letters, spaces, and dashes.
    - email: Must be in a valid email format.
    - phone: Must contain exactly 10 characters.
    - password: Must contain a minimum of 8 characters
    """
    # Extract request data, expecting JSON containing 'email', 'password', 'name', and 'phone'
    body_data = request.get_json()
    
    # Creates new user with validated data
    # Password is hashed for security
    validated_data = validate_data(user_registration_schema, body_data)

    user = User(
        name=validated_data.get('name'),
        email=validated_data.get('email'),
        phone=validated_data.get('phone'),
        password=hash_password(validated_data['password'])
    )  

    db.session.add(user)
    db.session.commit()
    
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
    
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    
    # Check if a user was found and the password matches hashed password in database
    # Generate a JWT token for the authenticated user, setting the token's expiry to 1 day
    if user and bcrypt.check_password_hash(user.password, body_data["password"]):
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        return {"email": user.email, "token": token, "is_admin": user.is_admin}
    else:
        abort(401)

@auth_bp.route("/users", methods=["GET"]) # View all users (as an admin)
@jwt_required() 
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
    
    return users_schema.dump(users), 200

@auth_bp.route("/user/<int:user_id>", methods=["GET"]) # Account holder or admin can view single account/ their own account
@jwt_required()
@load_current_user
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
    current_user = g.current_user

    # Check if the current user is trying to access their own data or is an admin, if not return error
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)

    # Retrieve the user object for the specified user_id
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    return user_schema.dump(user), 200

@auth_bp.route("/update", methods=["PUT"])  # Update user
@jwt_required()
@load_current_user
def update_account():
    """
    Updates the account details of the current user. The user must be authenticated via JWT.

    Allows the user to update their name, email, phone number, and password. Only the fields provided
    in the request body will be updated; omitted fields will retain their current values.

    Requires JWT authentication to identify the requesting user.

    Returns:
        - JSON object containing the updated user details with a 200 OK status.
        - A 404 Not Found error if the user with the specified JWT identity does not exist.

    Example request body:
    {
        "name": "New Name",
        "email": "new.email@email.com",
        "phone": "0412345699",
        "password": "newpassword"
    }
    Same Validation rules as "Register User" endpoint: 
    - name: Must contain only letters, spaces, and dashes.
    - email: Must be in a valid email format.
    - phone: Must contain exactly 10 characters.
    - password: Must contain a minimum of 8 characters
    """
    body_data = request.get_json()

    user = g.current_user
    
    validated_data = validate_data(UserSchema(partial=True), body_data)

    if 'password' in validated_data:
        validated_data['password'] = hash_password(validated_data['password'])

    # Iterates over each key-value pair in the validated data.
    # For each pair, it updates the corresponding attribute of the user object with the new value.
    # This dynamic allows for updating only the fields provided in the request body,
    # supporting partial updates. If a new password is provided, it's hashed before being set.
    for key, value in validated_data.items():
        setattr(user, key, value)

    db.session.commit()

    return user_schema.dump(user), 200

@auth_bp.route("/delete/<int:user_id>", methods=["DELETE"])  # Delete user
@jwt_required()
@load_current_user
def delete_account(user_id):
    """
    Deletes a specific user by their user ID. Can be accessed by an admin or 
    the user themselves wishing to delete their account.

    Requires JWT authentication. The token must belong to an admin or the user whose account 
    is being deleted.

    Returns:
        - A success message with a 200 OK status if the user was deleted.
        - A 401 Unauthorized error if a user is trying to delete an account that is not theirs, or an account that doesn't exist
        - A 403 Forbidden error if the requesting user is not authorised.
        - A 404 Not Found error if the user with the specified ID does not exist.
    """
    current_user = g.current_user
    
    # Check if the user is authorised to delete the account (either admin or the user)
    # If not, return an error
    if not current_user.is_admin and current_user.id != (user_id):
        abort(403)

    # Find the user to be deleted in the database or return an error
    user_to_delete = db.session.get(User, user_id)
    if not user_to_delete:
        abort(404)

    db.session.delete(user_to_delete)
    db.session.commit()
    
    return {"message": "User deleted successfully"}, 200

@auth_bp.route('/unlock_user/<int:user_id>', methods=['POST']) # Admin unlocks a user account
@jwt_required()
@authorise_as_admin
def unlock_user_account(user_id):
    user_to_unlock = User.query.get(user_id)
    if not user_to_unlock:
        abort(404)

    user_to_unlock.is_locked = False  
    user_to_unlock.booking_attempts = 0
    db.session.commit()

    return {'message': f'User account {user_id} unlocked successfully'}, 200



