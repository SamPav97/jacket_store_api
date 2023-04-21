from flask import request
from flask_api import status
from flask_restx import Resource

from managers.guest import GuestManager
from models.models_restx import auth_ns, auth_model, auth_model_login
from schemas.requests.auth import RegisterSchemaRequest, LoginSchemaRequest
from utils.decorators import validate_schema


@auth_ns.route("/register")
class RegisterResource(Resource):
    @auth_ns.expect(auth_model, validate=True)
    @auth_ns.response(201, 'Token is returned')
    @validate_schema(RegisterSchemaRequest)
    def post(self):
        data = request.get_json()
        existing_user = GuestManager.get_user_by_email(data['email'])
        if existing_user:
            return {'message': 'Email already exists'}, 409
        # For some reason the token returned by registration does not work, so I have to log in to get a working token.
        token = GuestManager.register(data)
        return {"token": token}, status.HTTP_201_CREATED


@auth_ns.route("/login")
class LoginResource(Resource):
    @auth_ns.expect(auth_model_login, validate=True)
    @auth_ns.response(200, 'Token is returned')
    @validate_schema(LoginSchemaRequest)
    def post(self):
        data = request.get_json()
        token = GuestManager.login(data)
        return {"token": token}, status.HTTP_200_OK
