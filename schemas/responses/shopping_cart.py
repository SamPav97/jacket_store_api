from marshmallow import Schema, fields
from schemas.responses.jacket import JacketSchemaResponse


class ShoppingCartSchemaResponse(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    jackets = fields.Nested(JacketSchemaResponse(many=True))
    amount = fields.Integer()
