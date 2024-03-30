from datetime import timedelta

from flask import Blueprint, request
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from init import db, bcrypt
from models.user import User, UserSchema, user_schema, users_schema, user_registration_schema
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
    """
    # Get user ID from the JWT token
    user_id = get_jwt_identity()
    body_data = request.get_json()

    # Retrieve the current user from the database
    user = db.session.get(User, user_id)
    if not user:
        # Return an error if the user does not exist
        return {"error": "User not found"}, 404

    try:
        # Validate incoming data with UserSchema, allowing partial updates.
        # This ensures that any fields provided in the request meet the validation criteria
        # defined in the UserSchema, such as minimum length for passwords or valid email format.
        validated_data = UserSchema(partial=True).load(body_data)
    except ValidationError as err:
        # If validation fails, return the specific validation error messages.
        return (err.messages), 400

    # Update user fields with validated data. Only fields that are provided in the request
    # and pass validation are updated. This ensures data integrity and adherence to 
    # validation rules even during updates.
    if 'name' in validated_data:
        user.name = validated_data['name']
    if 'email' in validated_data:
        user.email = validated_data['email']
    if 'phone' in validated_data:
        user.phone = validated_data['phone']
    if 'password' in validated_data and validated_data['password']:
        # The new password is hashed before storing to maintain security
        user.password = bcrypt.generate_password_hash(validated_data['password']).decode('utf-8')

    # Commit changes to the database
    db.session.commit()

    # Return updated user details
    return user_schema.dump(user), 200

@auth_bp.route("/delete/<int:user_id>", methods=["DELETE"])  # Delete user
@jwt_required()
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
    # Retrieve the ID of the current user from the JWT token
    current_user_id = get_jwt_identity()
    # Fetch user from database
    current_user = db.session.get(User, current_user_id)
    
    # Check if current_user is None
    if current_user is None:
        return {"error": "Authentication failed"}, 401

    # Check if the user is authorised to delete the account (either admin or the user)
    if not current_user.is_admin and current_user_id != str(user_id):
        return {"error": "Unauthorised"}, 403

    # Find the user to be deleted in the database
    user_to_delete = db.session.get(User, user_id)
    if not user_to_delete:
        # Return an error if no user is found with the provided ID
        return {"error": "User not found"}, 404

    # Delete the user from the database and commit the changes
    db.session.delete(user_to_delete)
    db.session.commit()
    
    # Return a success message
    return {"message": "User deleted successfully"}, 200


