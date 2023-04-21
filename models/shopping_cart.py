from db import db


class ShoppingCartModel(db.Model):
    __tablename__ = 'shopping_cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Integer, default=0)
    user = db.relationship("UserModel", back_populates="shopping_cart")
    jackets = db.relationship("JacketModel", secondary="shopping_cart_jackets", back_populates="shopping_carts")


shopping_cart_jackets = db.Table('shopping_cart_jackets',
                                 db.Column('shopping_cart_id', db.Integer, db.ForeignKey('shopping_cart.id'),
                                           primary_key=True),
                                 db.Column('jacket_id', db.Integer, db.ForeignKey('jacket.id'), primary_key=True)
                                 )
