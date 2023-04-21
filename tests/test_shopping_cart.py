from unittest.mock import patch

from flask_testing import TestCase

from config import create_app
from db import db
from managers.shopping_cart import ShoppingCartManager
from models import TransactionModel, ShoppingCartModel
from services.s3 import S3Service
from tests.factories import CreatorFactory
from tests.helpers import generate_token, sample_pic_of_cat


class TestShoppingCart(TestCase):
    url = "/shopping_cart"

    def create_app(self):
        return create_app("config.TestConfig")

    def setUp(self):
        # Set up the test database
        db.init_app(self.app)
        db.create_all()

    def tearDown(self):
        # Clean up the test database
        db.session.remove()
        db.drop_all()

    def test_get_jackets_from_shopping_cart_when_empty(self):
        user = CreatorFactory()
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        data = {}
        resp = self.client.get(self.url, headers=headers, json=data)

        expected_data = {
            "message": "Your shopping cart is empty"
        }

        self.assertEquals(resp.json, expected_data)

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_get_jackets_from_shopping_cart_when_jacket(self, mock_upload_photo):
        data_jacket = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        user = CreatorFactory()
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Create and add a jacket to jackets
        jacket = self.client.post("/jacket", headers=headers, json=data_jacket).json

        # Send jacket as body of put request
        data = {
            "jacket_id": 1
        }

        resp = self.client.put(self.url, headers=headers, json=data)

        # user_id is 0 because a user never gets created in the db.
        expected_data = {
            "user_id": 0,
            "amount": jacket['price'],
            "jackets": [
                {
                    "photo_url": jacket['photo_url'],
                    "created_on": jacket['created_on'],
                    "price": jacket['price'],
                    "description": jacket['description'],
                    "brand": jacket['brand'],
                    "size": jacket['size'],
                    "id": jacket['id']
                }
            ],
            "id": 1
        }

        self.assertEquals(sorted(resp.json), sorted(expected_data))

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_put_jacket_in_shopping_cart_when_no_data_in_request_body(self, mock_upload_photo):
        data_jacket = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        user = CreatorFactory()
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Create and add a jacket to jackets
        self.client.post("/jacket", headers=headers, json=data_jacket)

        # No jacket specified
        data = {
        }

        resp = self.client.put(self.url, headers=headers, json=data)

        expected_response = {
            "message": {
                "jacket_id": [
                    "Missing data for required field."
                ]
            }
        }

        self.assertEquals(resp.json, expected_response)

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_put_jacket_in_shopping_cart_when_wrong_jacket_id_in_data_in_request_body(self, mock_upload_photo):
        data_jacket = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        user = CreatorFactory()
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Create and add a jacket to jackets
        jacket = self.client.post("/jacket", headers=headers, json=data_jacket).json

        # Wrong id of jacket
        data = {
            "jacket_id": 9
        }

        resp = self.client.put(self.url, headers=headers, json=data)

        expected_response = {
            "message": "Jacket not found or already in the cart"
        }

        self.assertEquals(resp.json, expected_response)

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_delete_jacket_from_shopping_cart_happy_case(self, mock_upload_photo):
        data_jacket = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        user = CreatorFactory()
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Create and add a jacket to jackets
        self.client.post("/jacket", headers=headers, json=data_jacket)

        data = {
            "jacket_id": 1
        }

        self.client.put(self.url, headers=headers, json=data)

        cart = ShoppingCartModel.query.first()
        assert len(cart.jackets) == 1

        resp = self.client.delete(self.url, headers=headers, json=data)

        expected_response = {
            "amount": 0,
            "user_id": user.id,
            "jackets": [],
            "id": 1
        }

        self.assertEquals(resp.json, expected_response)

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_delete_jacket_from_shopping_cart_when_no_data_in_request_body(self, mock_upload_photo):
        data_jacket = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        user = CreatorFactory()
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Create and add a jacket to jackets
        self.client.post("/jacket", headers=headers, json=data_jacket)

        data_jacket_add_to_cart = {
            "jacket_id": 1
        }

        self.client.put(self.url, headers=headers, json=data_jacket_add_to_cart)

        cart = ShoppingCartModel.query.first()
        assert len(cart.jackets) == 1

        data_jacket_delete_from_cart = {
        }

        resp = self.client.delete(self.url, headers=headers, json=data_jacket_delete_from_cart)

        expected_response = {
            "message": {
                "jacket_id": [
                    "Missing data for required field."
                ]
            }
        }
        self.assertEquals(resp.json, expected_response)

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_delete_jacket_from_shopping_cart_when_wrong_jacket_id_in_data_in_request_body(self, mock_upload_photo):
        data_jacket = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        user = CreatorFactory()
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Create and add a jacket to jackets
        self.client.post("/jacket", headers=headers, json=data_jacket)

        data_jacket_add_to_cart = {
            "jacket_id": 1
        }

        self.client.put(self.url, headers=headers, json=data_jacket_add_to_cart)

        cart = ShoppingCartModel.query.first()
        assert len(cart.jackets) == 1

        data_jacket_delete_from_cart = {
            "jacket_id": 3
        }

        resp = self.client.delete(self.url, headers=headers, json=data_jacket_delete_from_cart)

        expected_response = {
            "message": "Jacket not found in the cart"
        }

        self.assertEquals(resp.json, expected_response)

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    @patch.object(
        ShoppingCartManager,
        "issue_transaction",
        return_value={
            "quote_id": "11-22",
            "recipient_id": "11",
            "transfer_id": "012",
            "target_account_id": "321",
            "amount": 10,
            "shopping_cart_id": 1,
        },
    )
    def test_cart_checkout_happy_case(self, mocked_transaction, mock_upload_photo):
        data_jacket = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        user = CreatorFactory()
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Create and add a jacket to jackets
        self.client.post("/jacket", headers=headers, json=data_jacket)

        data = {
            "jacket_id": 1
        }

        self.client.put(self.url, headers=headers, json=data)

        cart = ShoppingCartModel.query.first()
        cart_amount = cart.amount
        assert len(cart.jackets) == 1

        transactions = TransactionModel.query.all()
        assert len(transactions) == 0

        resp = self.client.post(self.url, headers=headers)

        assert resp.status_code == 200
        resp = resp.json

        expected_resp = {
            "message": "Purchase successful"
        }
        assert resp == expected_resp

        mocked_transaction.assert_called_once_with(
            user,
            cart_amount,
            f"{user.first_name} {user.last_name}",
            user.iban,
            cart.id,
        )

        transactions = TransactionModel.query.all()
        assert len(transactions) == 1

    def test_cart_checkout_empty_cart_purchase_failed(self):
        user = CreatorFactory()
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        self.client.get(self.url, headers=headers)

        cart = ShoppingCartModel.query.first()
        assert len(cart.jackets) == 0

        transactions = TransactionModel.query.all()
        assert len(transactions) == 0

        resp = self.client.post(self.url, headers=headers)

        assert resp.status_code == 400
        resp = resp.json

        expected_resp = {
            "message": "Purchase failed"
        }
        assert resp == expected_resp

        transactions = TransactionModel.query.all()
        assert len(transactions) == 0
