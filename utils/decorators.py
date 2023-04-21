from flask import request
from werkzeug.exceptions import BadRequest, Forbidden

from managers.auth import auth
from models import JacketSizes


def validate_schema(schema_name):
    def decorated_function(func):
        def wrapper(*args, **kwargs):
            data = request.get_json()
            # I get a string value in JSON that I have to turn into an enum object, so I do this here.
            # I am not sure that this is the right way to do this. The way I imagine it is that the front end will have
            # a drop-down menu where you select one of the size options, so a non-valid size would never be sent.
            if 'size' in data:
                size = JacketSizes[data["size"]]
                data["size"] = size
            schema = schema_name()
            errors = schema.validate(data)
            if not errors:
                return func(*args, **kwargs)
            raise BadRequest(errors)

        return wrapper

    return decorated_function


def permission_required(role):
    def decorated_function(func):
        def wrapper(*args, **kwargs):
            current_user = auth.current_user()
            if not current_user.role == role:
                raise Forbidden("Permission denied!")
            return func(*args, **kwargs)

        return wrapper

    return decorated_function
