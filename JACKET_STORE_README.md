API README

This RESTful API aims to be the backend for an online jacket shop, it is documented in Swagger 2.0 and has the following endpoints:
authentication, jacket management, shopping cart management. 

Third party integration: 
- The API is integrated with the payment provider WISE. Users are requested to provide their WISE keys upon registration to be able to use the API.
- The API is integrated with AWS s3 bucket to store all the pictures of jackets outside the server. 

The API consists of three main parts:

Authenticate: This part allows users to register and login.
Jacket: Responsible for jacket objects and their creation, deletion, etc.
Shopping cart: Responsible for user's shopping cart. Get current jacket, add, remove and purchase jackets.
The endpoint expects JSON format and returns an HTTP status code as a response.

The endpoints are:

authentication section
- /auth/login: POST method for user login.
- /auth/register: User registration POST method.

jacket section
- /jacket: POST method to create a new jacket.
- /Jacket: GET method to obtain a list of jackets. Optionally filter the jackets by brand using the brand query parameter.
- /jacket/{jacket_id}: PUT method to update a specific jacket.
- /jacket/{jacket_id}: DELETE method to remove a specific jacket.

shopping cart section
- /shopping_cart: POST method to purchase items in the cart. 
- /shopping_cart: PUT method to add a jacket to the cart.
- /shopping_cart: GET method to get the contents of the shopping cart.
- /shopping_cart: DELETE method to remove a jacket from the shopping cart.

Definitions
The API contains definitions for the following objects:
- user: Represents a user of your application, including personal and authentication information.
- register: Represents login credentials.
- jacket: Represents a jacket object with properties such as photo, brand, description, size, and price.
- shopping_cart: Represents a shopping cart object with properties such as amount, id, jackets, and user id. 