from resources.auth import RegisterResource, LoginResource
from resources.jacket import JacketsResource, JacketEditResource
from resources.shopping_cart import ShoppingCartResource

routes = (
    (RegisterResource, "/auth/register"),
    (LoginResource, "/auth/login"),
    (JacketsResource, "/jacket"),
    (JacketEditResource, "/jacket/<int:jacket_id>"),
    (ShoppingCartResource, "/shopping_cart"),
)
