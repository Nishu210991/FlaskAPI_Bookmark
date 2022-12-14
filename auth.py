from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED,HTTP_401_UNAUTHORIZED, HTTP_200_OK
from src.database import User, db
import validators
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity



auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post('/register')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if len(password)<6:
        return jsonify({"message":"Password is too short"}),HTTP_400_BAD_REQUEST

    if len(username)<3:
        return jsonify({"message":"Username is too short"}),HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username :
        return jsonify({"message":"username should be alphanumic also contain no space"}),HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"message":"email is already taken please try again"}),HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"message":"username is already taken please try again"}),HTTP_409_CONFLICT

    pwd_hash= generate_password_hash(password)

    user = User(username=username, email=email, password=pwd_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message":"User Created",
    "user": {
        'user':username,
        'email':email
    }
    }),HTTP_201_CREATED


@auth.post('/login')
def user_login():
    email = request.json.get('email','')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:
        is_password_correct = check_password_hash(user.password, password)
    
        if is_password_correct:
            refresh = create_refresh_token(identity=user.id)
            access  = create_access_token(identity=user.id)

            return jsonify({
                "user":
                {
                    "refresh" : refresh,
                    "access" : access,
                    "username": user.username,
                    "email": user.email

               }

            })

    return jsonify({
        "message": "Wrong Crediential are provided!!"
    }),HTTP_401_UNAUTHORIZED
            




@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "username": user.username,
        "email": user.email
    }), HTTP_200_OK

@auth.get("/token/refresh")
@jwt_required(refresh=True)
def get_refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        "access":access

    }), HTTP_200_OK

