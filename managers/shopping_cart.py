import uuid

from flask import abort
from sqlalchemy.orm import joinedload

from db import db
from models import ShoppingCartModel, JacketModel, TransactionModel
from services.wise import WiseService
from utils.encryptor import CryptoHelper


class ShoppingCartManager:

    @staticmethod
    def get_shopping_cart(user):
        shopping_cart = ShoppingCartModel.query.filter_by(user_id=user.id).first()
        if shopping_cart is None:
            shopping_cart = ShoppingCartModel(user_id=user.id)
            db.session.add(shopping_cart)
            db.session.flush()
        return shopping_cart

    @staticmethod
    def add_jacket(user, jacket_id):
        shopping_cart = ShoppingCartManager.get_shopping_cart(user)
        jacket = JacketModel.query.get(jacket_id)
        if jacket and jacket not in shopping_cart.jackets:
            shopping_cart.jackets.append(jacket)
            shopping_cart.amount += jacket.price
            db.session.flush()
            return shopping_cart
        return None

    @staticmethod
    def remove_jacket(user, jacket_id):
        shopping_cart = ShoppingCartManager.get_shopping_cart(user)
        jacket = JacketModel.query.get(jacket_id)
        if jacket and jacket in shopping_cart.jackets:
            shopping_cart.jackets.remove(jacket)
            shopping_cart.amount -= jacket.price
            db.session.flush()
            return shopping_cart
        return None

    @staticmethod
    def purchase(user):
        shopping_cart = ShoppingCartManager.get_shopping_cart(user)
        if shopping_cart.jackets:
            try:
                # Get jackets' IDs
                jacket_ids = [jacket.id for jacket in shopping_cart.jackets]

                # Query jackets with their creators' data
                jackets = JacketModel.query.options(joinedload(JacketModel.creator)).filter(JacketModel.id.in_(jacket_ids)).all()

                for jacket in jackets:
                    creator = jacket.creator
                    transaction_data = ShoppingCartManager.issue_transaction(
                        user,
                        jacket.price,
                        f"{creator.first_name} {creator.last_name}",
                        creator.iban,
                        shopping_cart.id
                    )
                    transaction = TransactionModel(**transaction_data)

                    db.session.delete(jacket)
                    db.session.add(transaction)

                shopping_cart.jackets = []
                shopping_cart.amount = 0
                db.session.flush()
                return True
            except Exception:
                # raise a 400 error with the exception message
                abort(400, "Your WISE key or IBAN are wrong")
        return False

    @staticmethod
    def issue_transaction(user, amount, full_name, iban, shopping_cart_id):
        crypto_helper = CryptoHelper()
        decrypted_wise_key = crypto_helper.decrypt(user.wise_key)
        wise = WiseService(decrypted_wise_key)
        quote_id = wise.create_quote("EUR", "EUR", amount)
        recipient_id = wise.create_recipient(full_name, iban)
        customer_transaction_id = str(uuid.uuid4())
        transfer_id = wise.create_transfer(recipient_id, quote_id, customer_transaction_id)["id"]
        data = {
            "quote_id": quote_id,
            "recipient_id": recipient_id,
            "transfer_id": transfer_id,
            "target_account_id": customer_transaction_id,
            "amount": amount,
            "shopping_cart_id": shopping_cart_id,
        }

        wise.fund_transfer(transfer_id)
        return data
