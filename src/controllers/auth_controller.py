from datetime import timedelta

from flask import Blueprint, request
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from init import db, bcrypt
from models.user import User, user_schema, users_schema, user_registration_schema

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route("/register", methods=["POST"]) # Register user
def auth_register():
    """
    Creates a new user account with details provided.

    Expects a JSON payload with the keys 'name', 'email', 'phone', and 'password'. 
    The 'password' is hashed before saving. If any of these keys are missing, 
    it will return a not nullable error.

    Returns:
        Tuple: A tuple containing the serialized user object and the HTTP status code 201, indicating successful creation.

    Example JSON:
    {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "0412345678",
        "password": "password"
    }
    """
    body_data = request.get_json()
    
    try:
        validated_data = user_registration_schema.load(body_data)
    except ValidationError as err:
        return (err.messages), 400

    user = User(
        name=validated_data.get('name'),
        email=validated_data.get('email'),
        phone=validated_data.get('phone'),
        password=bcrypt.generate_password_hash(validated_data.get('password')).decode('utf-8')
    )  

    db.session.add(user)
    db.session.commit()
    return user_schema.dump(user), 201
    
@auth_bp.route("/login", methods=["POST"]) # Login user
def auth_login():
    body_data = request.get_json()
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        return {"email": user.email, "token": token, "is_admin": user.is_admin}
    else:
        return {"error": "Invalid email or password"}, 401

@auth_bp.route("/users", methods=["GET"]) # Admin can view all users
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)
    if not current_user.is_admin:
        return {"error": "Access denied"}, 403

    users = db.session.query(User).all()
    return users_schema.dump(users), 200

@auth_bp.route("/user/<int:user_id>", methods=["GET"]) # Account holder or admin can view single account/ their own account
@jwt_required()
def get_user(user_id):
    current_user_id = int(get_jwt_identity()) 
    current_user = db.session.get(User, current_user_id)

    if current_user_id != user_id and not current_user.is_admin:
        return {"error": "Access denied"}, 403

    user = db.session.get(User, user_id)
    if not user:
        return {"error": "User not found"}, 404

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


