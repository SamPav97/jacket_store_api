from db import db
from models.enums import UserRole


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)
    phone = db.Column(db.String(14), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    iban = db.Column(db.String(22), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    wise_key = db.Column(db.String(255), nullable=False)
    # In case I want to get all jackets created by user:
    jackets = db.relationship("JacketModel", backref="jacket", lazy='dynamic')
    shopping_cart = db.relationship("ShoppingCartModel", back_populates="user", uselist=False)

