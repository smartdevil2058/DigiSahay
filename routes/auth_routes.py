
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request
)
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from extension import db
from model import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.post("/register")
def register():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body must be valid JSON"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    email = email.strip().lower()

    if not email or "@" not in email:
        return jsonify({
            "success": False,
            "message": "Enter a valid email address"
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 8 characters"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "Email is already registered"
        }), 409

    new_user = User(
        user_id=f"USR-{uuid4().hex[:12].upper()}",
        email=email,
        password_hash=generate_password_hash(password)
    )

    try:
        db.session.add(new_user)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Email is already registered"
        }), 409

    return jsonify({
        "success": True,
        "message": "Account created successfully",
        "user": {
            "user_id": new_user.user_id,
            "email": new_user.email,
            "preferred_language": new_user.preferred_language
        }
    }), 201


@auth_bp.post("/login")
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body must be valid JSON"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    email = email.strip().lower()

    user = User.query.filter_by(
        email=email
    ).first()

    if not user or not check_password_hash(
        user.password_hash, password
    ):
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=user.user_id
    )

    response = jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "preferred_language": user.preferred_language
        }
    })
    set_access_cookies(response, access_token)
    return response, 200


@auth_bp.post("/logout")
def logout():
    response = jsonify({
        "success": True,
        "message": "Logged out successfully"
    })
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.get("/check-session")
def check_session():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                "authenticated": False,
                "reason": "unauthenticated"
            }), 200

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({
                "authenticated": False,
                "reason": "user_not_found"
            }), 200

        return jsonify({
            "authenticated": True,
            "user": {
                "user_id": user.user_id,
                "email": user.email,
                "preferred_language": user.preferred_language
            }
        }), 200
    except ExpiredSignatureError:
        return jsonify({
            "authenticated": False,
            "reason": "expired"
        }), 401
    except Exception:
        return jsonify({
            "authenticated": False,
            "reason": "invalid"
        }), 401

@auth_bp.get("/me")
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "preferred_language": user.preferred_language
        }
    }), 200

