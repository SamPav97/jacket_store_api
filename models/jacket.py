from sqlalchemy import func

from db import db
from models.enums import JacketSizes


class JacketModel(db.Model):
    __tablename__ = 'jacket'

    id = db.Column(db.Integer, primary_key=True)
    photo_url = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, server_default=func.now())
    size = db.Column(db.Enum(JacketSizes), nullable=False, default=JacketSizes.m)
    price = db.Column(db.Integer, nullable=False, default=0)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    pic_hash = db.Column(db.String(), nullable=False)
    # In case I want to get the creator of the jacket without a join statement:
    creator = db.relationship("UserModel")
    # Get all shopping carts an instance of this model is in by jacket.shopping_carts
    shopping_carts = db.relationship("ShoppingCartModel", secondary="shopping_cart_jackets", back_populates="jackets")
