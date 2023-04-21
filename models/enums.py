from enum import Enum


# As far as I understand, we use enums to save smaller values in db and still be able to return full values.
# If this is correct then the enum below is somewhat useless?
class UserRole(Enum):
    guest = "guest"
    creator = "creator"
    admin = "admin"


class JacketSizes(Enum):
    xs = "XSmall"
    s = "Small"
    m = "Medium"
    l = "Large"
