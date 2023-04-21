from flask import request
from flask_api import status
from flask_restx import Resource

from managers.auth import auth
from managers.jacket import JacketManager
from models import UserRole
from models.models_restx import jacket_ns, jacket_model, brand_parser
from schemas.requests.jacket import JacketSchemaRequest
from schemas.responses.jacket import JacketSchemaResponse
from utils.decorators import permission_required, validate_schema


@jacket_ns.route("")
class JacketsResource(Resource):
    @jacket_ns.doc('get_jackets', responses={200: ('Jackets', jacket_model)})
    @jacket_ns.expect(brand_parser, validate=False)
    @auth.login_required
    def get(self):
        user = auth.current_user()
        brand = request.args.get('brand', None)

        if brand:
            jackets = JacketManager.get_jackets_by_brand(user, brand)
        else:
            jackets = JacketManager.get_jackets(user)

        if jackets:
            return JacketSchemaResponse().dump(jackets, many=True)
        else:
            return f"No jackets yet"

    @jacket_ns.expect(jacket_model, validate=False)
    @jacket_ns.response(201, 'Jacket created')
    @auth.login_required
    @permission_required(UserRole.creator)
    @validate_schema(JacketSchemaRequest)
    def post(self):
        data = request.get_json()
        current_user = auth.current_user()
        new_jacket = JacketManager.create(data, current_user)
        return JacketSchemaResponse().dump(new_jacket), status.HTTP_201_CREATED


# I create a separate class for working with requests for specific jackets because Flask won't let me use the same class
# for different routes, unlike Django.
@jacket_ns.route("/<int:jacket_id>")
@jacket_ns.param('jacket_id', 'The jacket identifier')
class JacketEditResource(Resource):
    # @auth.login_required
    # def get(self, jacket_id):
    #     jacket = JacketManager.get_jacket_by_id(jacket_id)
    #     if jacket and jacket.creator_id == auth.current_user().id:
    #         return JacketSchemaResponse().dump(jacket)
    #     else:
    #         return {'message': 'Jacket not found or not owned by the user'}, status.HTTP_404_NOT_FOUND

    @jacket_ns.doc('update_jacket', responses={200: ('Updated Jacket', jacket_model),
                                               404: 'Jacket not found or not owned by the user'})
    @jacket_ns.expect(jacket_model, validate=False)
    @auth.login_required
    @validate_schema(JacketSchemaRequest)
    def put(self, jacket_id):
        user = auth.current_user()
        data = request.get_json()

        edited_jacket = JacketManager.edit(jacket_id, data, user.id)
        if edited_jacket is None:
            return {'message': 'Jacket not found or not owned by the user'}, status.HTTP_404_NOT_FOUND

        return JacketSchemaResponse().dump(edited_jacket), status.HTTP_200_OK

    @jacket_ns.doc('delete_jacket',
                   responses={200: 'Jacket successfully deleted', 404: 'Jacket not found or not owned by the user'})
    @auth.login_required
    def delete(self, jacket_id):
        user = auth.current_user()
        is_deleted = JacketManager.delete(jacket_id, user.id)
        if is_deleted:
            return {'message': 'Jacket successfully deleted'}, status.HTTP_200_OK
        else:
            return {'message': 'Jacket not found or not owned by the user'}, status.HTTP_404_NOT_FOUND
