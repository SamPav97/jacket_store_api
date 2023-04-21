from marshmallow import fields, validate
from marshmallow_enum import EnumField

from models.enums import UserRole
from schemas.base import AuthBase


class RegisterSchemaRequest(AuthBase):
    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=20))
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=20))
    phone = fields.Str(required=True, validate=validate.Length(min=14, max=14))
    role = EnumField(UserRole, by_value=True)
    iban = fields.String(min_length=22, max_length=22, required=True)
    wise_key = fields.Str(required=True)


class LoginSchemaRequest(AuthBase):
    pass
