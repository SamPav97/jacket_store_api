# schemas/base.py
from marshmallow import Schema, fields


class ShoppingCartBase(Schema):
    jacket_id = fields.Integer(required=True)
    amount = fields.Integer()
