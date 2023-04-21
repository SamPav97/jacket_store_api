from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField

from models import JacketSizes


class AuthBase(Schema):
    email = fields.Email(required=True, unique=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=20))


class JacketBase(Schema):
    brand = fields.Str(required=True)
    description = fields.Str(required=True)
    size = EnumField(JacketSizes, by_value=True)
    price = fields.Int(required=True)
