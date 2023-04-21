import os
import uuid

from werkzeug.exceptions import Unauthorized

from common.constants import TEMP_DIR
from db import db
from models import JacketModel
from services.s3 import S3Service
from utils.encryptor import decode_file, generate_image_hash


class JacketManager:
    @staticmethod
    def _get_jacket_by_id(jacket_id):
        return db.session.query(JacketModel).filter(JacketModel.id == jacket_id).first()

    @staticmethod
    def _decode_and_save_temp_image(photo, extension):
        file_name = f"{str(uuid.uuid4())}.{extension}"
        path = os.path.join(TEMP_DIR, file_name)
        decode_file(path, photo)
        return file_name, path

    @staticmethod
    def _process_image(photo, extension, old_photo_url=None):
        file_name, path = JacketManager._decode_and_save_temp_image(photo, extension)
        pic_hash = generate_image_hash(path)

        s3 = S3Service()

        if old_photo_url:
            old_photo_name = old_photo_url.split("/")[-1]
            s3.delete_photo(old_photo_name)

        photo_url = s3.upload_photo(path, file_name)
        os.remove(path)

        return pic_hash, photo_url

    @staticmethod
    def get_jackets(user):
        return JacketModel.query.all()

    @staticmethod
    def get_jackets_by_brand(user, brand):
        return JacketModel.query.filter_by(creator_id=user.id, brand=brand).all()

    @staticmethod
    def create(data, user):
        data["creator_id"] = user.id
        extension = data.pop("extension")
        photo = data.pop("photo")

        pic_hash, photo_url = JacketManager._process_image(photo, extension)

        data['pic_hash'] = pic_hash
        data["photo_url"] = photo_url

        jacket = JacketModel(**data)
        db.session.add(jacket)
        db.session.flush()
        return jacket

    @staticmethod
    def edit(jacket_id, data, user):
        jacket = JacketManager._get_jacket_by_id(jacket_id)
        if not jacket:
            return None

        if jacket.creator_id != user:
            raise Unauthorized("You do not own this jacket")

        extension = data.pop("extension")
        photo = data.pop("photo")
        file_name, path = JacketManager._decode_and_save_temp_image(photo, extension)
        new_pic_hash = generate_image_hash(path)

        if new_pic_hash != jacket.pic_hash:
            new_photo_url = JacketManager._process_image(photo, extension, jacket.photo_url)
            jacket.pic_hash = new_pic_hash
            jacket.photo_url = new_photo_url
        else:
            os.remove(path)

        editable_fields = ['brand', 'description', 'size']

        for key, value in data.items():
            if key in editable_fields:
                setattr(jacket, key, value)

        db.session.flush()
        return jacket

    @staticmethod
    def delete(jacket_id, user_id):
        s3 = S3Service()
        # In this request I make sure the owner is same as user who requests delete.
        jacket = JacketModel.query.filter_by(id=jacket_id, creator_id=user_id).first()
        if jacket:
            photo_name = jacket.photo_url.split("/")[-1]
            s3.delete_photo(photo_name)
            db.session.delete(jacket)
            db.session.flush()
            return True
        return False

