from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth import AuthManager
from models.user import UserModel
from utils.encryptor import CryptoHelper


class GuestManager:
    @staticmethod
    def register(guest_data):
        guest_data["password"] = generate_password_hash(guest_data["password"])
        crypto_helper = CryptoHelper()
        encrypted_wise_key = crypto_helper.encrypt(guest_data["wise_key"])
        guest_data["wise_key"] = encrypted_wise_key

        user = UserModel(**guest_data)
        db.session.add(user)
        db.session.commit()
        guest = UserModel.query.filter_by(email=user.email).first()
        return AuthManager.encode_token(guest)

    @staticmethod
    def login(login_data):
        guest = UserModel.query.filter_by(email=login_data["email"]).first()
        if not guest:
            raise BadRequest("No such email! Please register!")

        if check_password_hash(guest.password, login_data["password"]):
            return AuthManager.encode_token(guest)
        raise BadRequest("Wrong credentials!")

    @staticmethod
    def get_user_by_email(email):
        return UserModel.query.filter_by(email=email).first()
