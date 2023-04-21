from flask import request
from flask_api import status
from flask_restx import Resource

from managers.auth import auth
from managers.shopping_cart import ShoppingCartManager
from models.models_restx import shopping_cart_ns, shopping_cart_model, jacket_id_model
from schemas.responses.shopping_cart import ShoppingCartSchemaResponse
from schemas.shopping_cart_base import ShoppingCartBase
from utils.decorators import validate_schema


@shopping_cart_ns.route("")
class ShoppingCartResource(Resource):
    @shopping_cart_ns.doc('get_shopping_cart',
                          responses={200: ('Shopping Cart', shopping_cart_model), 204: 'Your shopping cart is empty'})
    @auth.login_required
    def get(self):
        user = auth.current_user()
        shopping_cart = ShoppingCartManager.get_shopping_cart(user)
        if len(shopping_cart.jackets) >= 1:
            return ShoppingCartSchemaResponse().dump(shopping_cart), status.HTTP_200_OK
        else:
            return {'message': 'Your shopping cart is empty'}

    @shopping_cart_ns.doc('add_jacket_to_cart', responses={200: ('Jacket added', shopping_cart_model), 404: 'Jacket not found or already in the cart'})
    @shopping_cart_ns.expect(jacket_id_model, validate=False)
    @auth.login_required
    @validate_schema(ShoppingCartBase)
    def put(self):
        data = request.get_json()
        user = auth.current_user()
        shopping_cart = ShoppingCartManager.add_jacket(user, data['jacket_id'])
        if shopping_cart:
            return ShoppingCartSchemaResponse().dump(shopping_cart), status.HTTP_200_OK
        else:
            return {'message': 'Jacket not found or already in the cart'}, status.HTTP_404_NOT_FOUND

    @shopping_cart_ns.doc('remove_jacket_from_cart', responses={200: ('Jacket removed', shopping_cart_model), 404: 'Jacket not found in the cart'})
    @shopping_cart_ns.expect(jacket_id_model, validate=False)
    @auth.login_required
    @validate_schema(ShoppingCartBase)
    def delete(self):
        data = request.get_json()
        user = auth.current_user()
        shopping_cart = ShoppingCartManager.remove_jacket(user, data['jacket_id'])
        if shopping_cart:
            return ShoppingCartSchemaResponse().dump(shopping_cart), status.HTTP_200_OK
        else:
            return {'message': 'Jacket not found in the cart'}, status.HTTP_404_NOT_FOUND

    @shopping_cart_ns.doc('purchase', responses={200: 'Purchase successful', 400: 'Purchase failed'})
    @auth.login_required
    def post(self):
        user = auth.current_user()
        success = ShoppingCartManager.purchase(user)
        if success:
            return {'message': 'Purchase successful'}, status.HTTP_200_OK
        else:
            return {'message': 'Purchase failed'}, status.HTTP_400_BAD_REQUEST
