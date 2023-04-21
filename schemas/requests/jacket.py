from schemas.base import JacketBase
from marshmallow import fields


class JacketSchemaRequest(JacketBase):
    photo = fields.String(required=True)
    extension = fields.String(required=True)
