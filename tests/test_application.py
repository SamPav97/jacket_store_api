from unittest.mock import patch

from flask_testing import TestCase

from config import create_app
from db import db
from models import UserModel
from services.s3 import S3Service
from tests.factories import GuestFactory, CreatorFactory
from tests.helpers import generate_token, sample_pic_of_cat

ENDPOINTS_DATA = (
    ("/jacket", "GET"),
    ("/jacket", "POST"),
    ("/jacket/1", "PUT"),
    ("/jacket/1", "DELETE"),
)


class TestApp(TestCase):
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

    def iterate_endpoints(self, endpoints_data, status_code_method, expected_resp_body, headers=None, payload=None):
        if not headers:
            headers = {'Content-Type': 'application/json'}
        if not payload:
            payload = {
                "photo": sample_pic_of_cat,
                "extension": "jpg",
                "brand": "Armani",
                "description": "This is a great jacket!",
                "size": "l",
                "price": 100
            }

        # Iterate through the provided endpoints and methods, sending requests and checking the responses
        for url, method in endpoints_data:
            print(f"Testing {method} {url} with headers: {headers} and payload: {payload}")
            if method == "GET":
                payload = {}
                resp = self.client.get(url, headers=headers)
            elif method == "POST":
                resp = self.client.post(url, headers=headers, data=payload)
            elif method == "PUT":
                resp = self.client.put(url, headers=headers, data=payload)
            elif method == "DELETE":
                resp = self.client.delete(url, headers=headers, data=payload)
            status_code_method(resp)
            self.assertEqual(resp.json, expected_resp_body)

    def test_login_required(self):
        # Test that all endpoints require a valid login
        self.iterate_endpoints(
            ENDPOINTS_DATA, self.assert_401, {"message": "Missing token"},
        )

    def test_invalid_token_raises(self):
        # Test that an invalid token results in a 401 error
        headers = {"Authorization": "Bearer eyJ0eX"}
        self.iterate_endpoints(
            ENDPOINTS_DATA, self.assert_401, {"message": "Invalid token"}, headers
        )

    def test_missing_permissions_for_editor_raises(self):
        # Test that guests cannot perform actions that require the creator role
        data = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }
        endpoints = (
            ("/jacket/1", "PUT"),
            ("/jacket/1", "DELETE"),
        )
        user = GuestFactory()
        token = generate_token(user)
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {token}"}

        for url, method in endpoints:
            if method == "PUT":
                resp = self.client.put(url, headers=headers, json=data)
            self.assert404(resp)
            self.assertEqual(resp.json, {'message': 'Jacket not found'})

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_get_all_happy_case(self, mock_upload_photo):
        create_data_1 = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }
        create_data_2 = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "armani",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        expected_data = [
            {
                "created_on": "2023-04-19T12:41:34.047926",
                "description": "This is a great jacket!",
                "price": 100,
                "id": 1,
                "brand": "marccain",
                "photo_url": "https://jacket-api-bucket.s3.eu-north-1.amazonaws.com/3d7eea87-fa7a-4738-9a51-023800f887bc.jpg",
                "size": "Large"
            },
            {
                "created_on": "2023-04-19T12:41:49.116909",
                "description": "This is a great jacket!",
                "price": 100,
                "id": 2,
                "brand": "armani",
                "photo_url": "https://jacket-api-bucket.s3.eu-north-1.amazonaws.com/4a909430-7c4b-4be9-904d-f26bb994ab42.jpg",
                "size": "Large"
            }
        ]

        user = CreatorFactory()
        token = generate_token(user)
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {token}"}

        # Create a new jacket
        post_url = "/jacket"
        self.client.post(post_url, headers=headers, json=create_data_1)
        self.client.post(post_url, headers=headers, json=create_data_2)

        resp = self.client.get(post_url, headers=headers)

        self.assertEqual(resp.json[0]['id'], expected_data[0]['id'])
        self.assertEqual(resp.json[1]['id'], expected_data[1]['id'])

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_get_by_brand_happy_case(self, mock_upload_photo):
        create_data_1 = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }
        create_data_2 = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "armani",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        expected_data = [
            {
                "created_on": "2023-04-19T12:41:34.047926",
                "description": "This is a great jacket!",
                "price": 100,
                "id": 1,
                "brand": "marccain",
                "photo_url": "https://jacket-api-bucket.s3.eu-north-1.amazonaws.com/3d7eea87-fa7a-4738-9a51-023800f887bc.jpg",
                "size": "Large"
            },
            {
                "created_on": "2023-04-19T12:41:49.116909",
                "description": "This is a great jacket!",
                "price": 100,
                "id": 2,
                "brand": "armani",
                "photo_url": "https://jacket-api-bucket.s3.eu-north-1.amazonaws.com/4a909430-7c4b-4be9-904d-f26bb994ab42.jpg",
                "size": "Large"
            }
        ]

        user = CreatorFactory()
        token = generate_token(user)
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {token}"}

        # Create a new jacket
        post_url = "/jacket"
        self.client.post(post_url, headers=headers, json=create_data_1)
        self.client.post(post_url, headers=headers, json=create_data_2)

        get_url = "/jacket?brand=armani"
        resp = self.client.get(get_url, headers=headers)

        self.assertEqual(len(resp.json), 1)
        self.assertEqual(resp.json[0]['id'], expected_data[1]['id'])

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_successful_edit(self, mock_upload_photo):
        create_data = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }
        edit_data = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "New Brand",
            "description": "This is an edited jacket!",
            "size": "m",
            "price": 100
        }

        user = CreatorFactory()
        token = generate_token(user)
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {token}"}

        # Create a new jacket
        post_url = "/jacket"
        created_resp = self.client.post(post_url, headers=headers, json=create_data)

        # Get the ID of the created jacket
        created_jacket_id = created_resp.json['id']

        # Edit the created jacket
        put_url = f"/jacket/{created_jacket_id}"
        edited_resp = self.client.put(put_url, headers=headers, json=edit_data)

        # Check if the response status is OK
        self.assertStatus(edited_resp, 200)

        # Check if the response contains the updated fields
        self.assertEqual(edited_resp.json['id'], created_jacket_id)
        # self.assertEqual(edited_resp.json['photo_url'], edit_data['photo_url'])
        self.assertEqual(edited_resp.json['brand'], edit_data['brand'])
        self.assertEqual(edited_resp.json['description'], edit_data['description'])
        self.assertEqual(edited_resp.json['size'], 'Medium')

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_successful_delete(self, mock_upload_photo):
        create_data = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }

        user = CreatorFactory()
        token = generate_token(user)
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {token}"}

        # Create a new jacket
        post_url = "/jacket"
        created_resp = self.client.post(post_url, headers=headers, json=create_data)

        # Get the ID of the created jacket
        created_jacket_id = created_resp.json['id']

        # Delete the created jacket
        delete_url = f"/jacket/{created_jacket_id}"
        delete_resp = self.client.delete(delete_url, headers=headers)

        # Check if the response status is OK
        self.assertStatus(delete_resp, 200)

        # Check if the jacket is indeed deleted
        get_url = f"/jacket"
        get_resp = self.client.get(get_url, headers=headers)
        self.assert200(get_resp)
        self.assertEqual(get_resp.json, "No jackets yet")

    def test_post_jacket_permission_denied_for_non_creator_user_role(self):
        # Test that guests cannot create a new jacket
        data = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }
        post_url = "/jacket"
        user = GuestFactory()
        token = generate_token(user)
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {token}"}

        resp = self.client.post(post_url, headers=headers, json=data)
        self.assert403(resp)
        self.assertEqual(resp.json, {'message': 'Permission denied!'})

    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_post_jacket_happy_case(self, mock_upload_photo):
        data = {
            "photo": sample_pic_of_cat,
            "extension": "jpg",
            "brand": "Marccain",
            "description": "This is a great jacket!",
            "size": "l",
            "price": 100
        }
        post_url = "/jacket"
        user = CreatorFactory()
        token = generate_token(user)
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {token}"}
        resp = None

        resp = self.client.post(post_url, headers=headers, json=data)
        self.assertStatus(resp, 201)

        # Check if the response contains the expected fields
        self.assertIn('id', resp.json)
        # self.assertEqual(resp.json['photo_url'], data['photo_url'])
        self.assertEqual(resp.json['brand'], data['brand'])
        self.assertEqual(resp.json['description'], data['description'])
        self.assertEqual(resp.json['size'], 'Large')

    def test_register_schema_raises_invalid_first_name(self):
        data = {"last_name": "Test", "email": "test@test.com", "phone": "11111111111111", "password": "12345@assd1",
                "iban": "DE89370400440532013000",
                "wise_key": "8db48ad2-7b7c-44d1-bcf6-fc300481c851"}
        headers = {"Content-Type": "application/json"}
        url = "/auth/register"

        # Missing name
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'first_name': ['Missing data for required field.']}}

        data["first_name"] = "A"
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'first_name': ['Length must be between 2 and 20.']}}

        data["first_name"] = "AAAAAAAAAAAAAAAAAAAAAAA"
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'first_name': ['Length must be between 2 and 20.']}}

    def test_register_schema_raises_invalid_last_name(self):
        data = {"first_name": "Test", "email": "test@test.com", "phone": "11111111111111", "password": "12345@assd1",
                "iban": "DE89370400440532013000",
                "wise_key": "8db48ad2-7b7c-44d1-bcf6-fc300481c851"}
        headers = {"Content-Type": "application/json"}
        url = "/auth/register"

        # Missing last_name
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'last_name': ['Missing data for required field.']}}

        # Invalid last_name length
        data["last_name"] = "A"
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'last_name': ['Length must be between 2 and 20.']}}

        data["last_name"] = "AAAAAAAAAAAAAAAAAAAAAAA"
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'last_name': ['Length must be between 2 and 20.']}}

    def test_register_schema_raises_invalid_phone(self):
        data = {"first_name": "Test", "last_name": "User", "email": "test@test.com", "password": "12345@assd1",
                "iban": "DE89370400440532013000",
                "wise_key": "8db48ad2-7b7c-44d1-bcf6-fc300481c851"}
        headers = {"Content-Type": "application/json"}
        url = "/auth/register"

        # Missing phone
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'phone': ['Missing data for required field.']}}

        # Invalid phone length
        data["phone"] = "1111111111111"
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'phone': ['Length must be between 14 and 14.']}}

        data["phone"] = "111111111111111"
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'phone': ['Length must be between 14 and 14.']}}

    def test_register_schema_raises_invalid_password(self):
        data = {"first_name": "Test", "last_name": "User", "email": "test@test.com", "phone": "11111111111111",
                "iban": "DE89370400440532013000",
                "wise_key": "8db48ad2-7b7c-44d1-bcf6-fc300481c851"}
        headers = {"Content-Type": "application/json"}
        url = "/auth/register"

        # Missing password
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'password': ['Missing data for required field.']}}

        # Invalid password length
        data["password"] = "12345"
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'password': ['Length must be between 8 and 20.']}}

        data["password"] = "123456789012345678901"
        resp = self.client.post(url, headers=headers, json=data)
        self.assert400(resp)
        assert resp.json == {'message': {'password': ['Length must be between 8 and 20.']}}

    def test_register_schema_happy_case(self):
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "phone": "11111111111111",
            "password": "12345@assd1",
            "role": "guest",
            "iban": "DE89370400440532013000",
            "wise_key": "8db48ad2-7b7c-44d1-bcf6-fc300481c851"
        }
        headers = {"Content-Type": "application/json"}
        url = "/auth/register"

        # Happy case - all fields are valid
        resp = self.client.post(url, headers=headers, json=data)
        self.assert_status(resp, 201)

        # Check if user is in the database
        created_user = UserModel.query.filter_by(email=data["email"]).first()
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.first_name, data["first_name"])
        self.assertEqual(created_user.last_name, data["last_name"])
        self.assertEqual(created_user.email, data["email"])
        self.assertEqual(created_user.phone, data["phone"])
