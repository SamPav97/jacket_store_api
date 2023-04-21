from random import randint

import factory

from db import db
from models import UserModel, UserRole


class BaseFactory(factory.Factory):

    class Meta:
        model = UserModel
    id = factory.Sequence(lambda n: n)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = str(randint(100000, 200000))
    password = factory.Faker("password")
    iban = factory.Faker("iban")
    wise_key = "8db48ad2-7b7c-44d1-bcf6-fc300481c851"

    @classmethod
    def create(cls, **kwargs):
        object = super().create(**kwargs)
        db.session.add(object)
        db.session.commit()
        return object


class GuestFactory(BaseFactory):
    role = UserRole.guest


class CreatorFactory(BaseFactory):
    role = UserRole.creator

