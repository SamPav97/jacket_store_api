from flask_restx import Namespace, fields, reqparse

jacket_ns = Namespace("jacket", description="Jacket related operations")
jacket_model = jacket_ns.model('jacket', {'photo': fields.String('Base64 codified image.'),
                                          'extension': fields.String('File extension of image'),
                                          'brand': fields.String('Sample brand'),
                                          'description': fields.String('Description of jacket'),
                                          'size': fields.String('xs,s,m,l'),
                                          'price': fields.Integer()})

shopping_cart_ns = Namespace("shopping_cart", description="Shopping cart related operations")

shopping_cart_model = shopping_cart_ns.model('shopping_cart', {
    'amount': fields.Float(description='Total amount of the shopping cart'),
    'id': fields.Integer(description='Shopping cart identifier'),
    'jackets': fields.List(fields.Nested(jacket_model), description='List of jackets in the shopping cart'),
    'user_id': fields.Integer(description='User identifier')
})

jacket_id_model = shopping_cart_ns.model('jacket_id', {
    'jacket_id': fields.Integer(description='The jacket identifier', required=True)
})

auth_ns = Namespace("auth", description="Authentication related operations")
auth_model = auth_ns.model('user', {'first_name': fields.String('Ivan'),
                                    'last_name': fields.String('Ivanov'),
                                    'email': fields.String('Email for user'),
                                    'phone': fields.String('Phone number for user'),
                                    'password': fields.String('Password for user'),
                                    'role': fields.String('User is either guest or creator'),
                                    'iban': fields.String('Iban of user'),
                                    'wise_key': fields.String('Wise key of user')
                                    })

auth_model_login = auth_ns.model('login', {'email': fields.String('Email of user'),
                                           'password': fields.String('Password for user')})


# Define the query parameters parser
brand_parser = reqparse.RequestParser()
brand_parser.add_argument('brand', type=str, help='Filter jackets by brand')