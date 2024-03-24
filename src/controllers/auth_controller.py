from datetime import timedelta

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from psycopg2 import errorcodes

from init import db, bcrypt
from models.user import User, user_schema, users_schema

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route("/register", methods=["POST"]) # /auth/register
def auth_register():
    try:
        body_data = request.get_json()

        user = User(
            name=body_data.get('name'),
            email=body_data.get('email'),
            phone=body_data.get('phone')
        )

        password = body_data.get('password')
        if password:
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')

        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 201
    
    except IntegrityError as err:
        print(err.orig.pgcode)
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400
        
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Email already in use"}, 409
    
@auth_bp.route("/login", methods=["POST"]) # /auth/login
def auth_login():
    body_data = request.get_json()
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        return {"email": user.email, "token": token, "is_admin": user.is_admin}
    else:
        return {"error": "Invalid email or password"}, 401

@auth_bp.route("/users", methods=["GET"])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)
    if not current_user.is_admin:
        return {"error": "Access denied"}, 403

    users = db.session.query(User).all()
    return users_schema.dump(users), 200

@auth_bp.route("/update", methods=["PUT"])  # /auth/update
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

    db.session.commit()
    return user_schema.dump(user), 200

@auth_bp.route("/delete/<int:user_id>", methods=["DELETE"])  # /auth/delete/<user_id>
@jwt_required()
def delete_account(user_id):
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    # Ensure the current user is admin or trying to delete their own account
    if not current_user.is_admin and current_user_id != str(user_id):
        return {"error": "Unauthorised"}, 403

    user_to_delete = db.session.get(User, user_id)
    if not user_to_delete:
        return {"error": "User not found"}, 404

    db.session.delete(user_to_delete)
    db.session.commit()
    return {"message": "User deleted successfully"}, 200


