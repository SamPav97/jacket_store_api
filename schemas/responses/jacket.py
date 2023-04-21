from marshmallow import fields

from schemas.base import JacketBase


class JacketSchemaResponse(JacketBase):
    id = fields.Int(required=True)
    created_on = fields.DateTime(required=True)
    photo_url = fields.String(required=True)
