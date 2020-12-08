# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Wishlist Service

Paths:
------
GET /wishlists - returns a list all of the wishlists
GET /wishlists/{wishlist_id} - returns the wishlist with a given id number
POST /wishlists - creates a new wishlist record in the database
PUT /wishlists/{wishlist_id} - updates a wishlist record in the database
DELETE /wishlists/{wishlist_id} - deletes a wishlist record in the database
PUT /wishlists/{wishlist_id}/enabled - enables a wishlist record in the database
PUT /wishlists/{wishlist_id}/disabled - disables a wishlist record in the database
GET /wishlists/{wishlist_id}/items - returns a list all the items of the given wishlist
POST /wishlists/{wishlist_id}/items - creates an item in the given wishlist
GET /wishlists/{wishlist_id}/items/{item_id} - returns an item with item id
                                                in the given wishlist
DELETE /wishlists/{wishlist_id}/items/{item_id} - deletes an item with item id
                                                    in the given wishlist
"""

from flask import jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound
from flask_restplus import Api, Resource, fields, reqparse, inputs

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from service.models import Wishlist, Item, DataValidationError

# Import Flask application
from . import app


@app.route('/items.html')
def items():
    """ Loads the items.html page """
    return app.send_static_file('items.html')


@app.route('/')
def homepage():
    """ Loads the homepage (wishlist) page """
    return app.send_static_file('index.html')


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Wishlist REST API Service',
          description='This is a wishlist service for an e-commerce',
          default='wishlists',
          default_label='Wishlist operations',
          doc='/apidocs/index.html',  # default also could use doc='/apidocs/index.html'
          )

# Define the model so that the docs reflect what can be sent
item_model = api.model('Item', {
    'id': fields.Integer(readOnly=True,
                        description='The unique id assigned internally by service'),
    'wishlist_id': fields.Integer(required=True,
                                 description='Wishlist id of the item'),
    'product_id': fields.Integer(required=True,
                                description='Id of the item'),
    'product_name': fields.String(required=True,
                                  description='Name of the item')
})

wishlist_model = api.model('Wishlist', {
    'id': fields.Integer(readOnly=True,
                         description='The unique id assigned internally by service'),
    'name': fields.String(required=True,
                          description='The name of the Wishlist'),
    'user_id': fields.Integer(required=True,
                              description='User id of the user to whom the wishlist belongs'),
    'status': fields.Boolean(required=False,
                             description='Status of the wishlist'),
    'items': fields.List(fields.Nested(item_model, required=True),
                         required=True,
                         description='List of items in the wishlist')
})

create_model = api.model('Wishlist', {
    'name': fields.String(required=True,
                          description='The name of the Wishlist'),
    'user_id': fields.Integer(required=True,
                              description='User id of the user to whom the wishlist belongs'),
    'items': fields.List(fields.Nested(item_model, required=True),
                         required=True,
                         description='List of items in the wishlist')
})

create_item_model = api.model('Item', {
    'wishlist_id': fields.Integer(required=True,
                                 description='Wishlist id of the item'),
    'product_id': fields.Integer(required=True,
                                description='Id of the item'),
    'product_name': fields.String(required=True,
                                  description='Name of the item')
})

# query string arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument('name', type=str, required=False, help='List wishlists by name')
wishlist_args.add_argument('user_id', type=int, required=False, help='List wishlists by user_id')


######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST,
            error="Bad Request",
            message=str(error)
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_404_NOT_FOUND,
            error="Not Found",
            message=str(error)
        ),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=str(error),
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=str(error),
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    app.logger.error(str(error))
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=str(error),
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

######################################################################
#  PATH: /wishlists/{wishlist_id}
######################################################################
@api.route('/wishlists/<int:wishlist_id>')
@api.param('wishlist_id', 'The wishlist identifier')
class WishlistResource(Resource):
    """
    WishlistResource class
    Allows the manipulation of a single Wishlist
    GET /Wishlist{id} - Returns a Wishlist with the id
    PUT /Wishlist{id} - Update a Wishlist with the id
    DELETE /Wishlist{id} -  Deletes a Wishlist with the id
    """

    ######################################################################
    # RETRIEVE A WISHLIST
    ######################################################################
    @api.doc('get_wishlists')
    @api.response(404, 'Wishlist not found')
    @api.marshal_with(wishlist_model) 
    def get(self, wishlist_id):
        """
        Retrieve a single Wishlist
        This endpoint will return a Wishlist based on its id
        """
        app.logger.info("Request for wishlist with id: %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))
        return wishlist.serialize(), status.HTTP_200_OK
       
    ######################################################################
    # UPDATE A WISHLIST
    ######################################################################
    @api.doc('update_wishlists')
    @api.response(404, 'Wishlist not found')
    @api.response(400, 'The posted Wishlist data was not valid')
    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Update a Wishlist
        This endpoint will update a Wishlist based the id specified in the path
        """
        app.logger.info("Request to update wishlist with id: %s", wishlist_id)
        check_content_type("application/json")
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        wishlist.deserialize(data)
        wishlist.id = wishlist_id
        wishlist.save()
        return wishlist.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A WISHLIST
    ######################################################################
    @api.doc('delete_wishlists')
    @api.response(204, 'Wishlist deleted')
    def delete(self, wishlist_id):
        """
        Delete a Wishlist
        This endpoint will delete a Wishlist based the id specified in the path
        """
        app.logger.info("Request to delete wishlist with id: %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()

        app.logger.info("Wishlist with ID [%s] delete complete.", wishlist_id)
        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists
######################################################################
@api.route('/wishlists', strict_slashes=False)
class WishlistCollection(Resource):
    """ Handles all interactions with collections of Wishlists """
    ######################################################################
    # LIST ALL WISHLISTS
    ######################################################################
    @api.doc('list_wishlists')
    @api.expect(wishlist_args, validate=True)
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """ Returns all of the Wishlists """
        app.logger.info("Request for wishlist list")
        if request.args:
            user_id = request.args.get("user_id")
            name = request.args.get("name")
            if user_id:
                try:
                    user_id = int(user_id)
                except ValueError:
                    raise DataValidationError("user_id should be an integer")
                wishlists = Wishlist.find_by_user_id(user_id)
            elif name:
                name = name.strip("\"\'")
                wishlists = Wishlist.find_by_name(name)
            else:
                raise DataValidationError("query parameter does not exist")
        else:
            wishlists = Wishlist.all()

        results = [wishlist.serialize() for wishlist in wishlists]
        app.logger.info("Returning %d wishlists", len(results))
        app.logger.debug("Results :%s", results)
        return results, status.HTTP_200_OK

    ######################################################################
    # ADD A NEW WISHLIST
    ######################################################################
    @api.doc('create_wishlist')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Wishlist created successfully')
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Creates a Wishlist
        This endpoint will create a Wishlist based the data in the posted body
        """
        app.logger.info("Request to create a wishlist")
        check_content_type("application/json")
        wishlist = Wishlist()
        app.logger.debug('Payload = %s', api.payload)
        wishlist.deserialize(api.payload)
        app.logger.debug('Deserialized wishlist = %s', wishlist)
        data = api.payload

        try:
            items = []
            for item in data["items"]:
                new_item = Item()
                items.append(new_item.deserialize(item))
            wishlist.items = items
        except KeyError as error:
            raise DataValidationError("Invalid Wishlist: missing " +
                                      error.args[0])

        app.logger.debug('Deserialized wishlist after adding items= %s',
                         wishlist)

        wishlist.create()
        message = wishlist.serialize()
        location_url = api.url_for(WishlistResource, 
                                    wishlist_id=wishlist.id, _external=True)
        return message, status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
#  PATH: /wishlists/{wishlist_id}/items
######################################################################
@api.route('/wishlists/<int:wishlist_id>/items', strict_slashes=False)
@api.param('wishlist_id', 'The wishlist identifier')
class ItemCollection(Resource):
    """ Handles all interactions with collections of Items """
    ######################################################################
    # LIST ITEMS FROM WISHLISTS
    ######################################################################
    @api.doc('list_items_in_the_wishlist')
    @api.response(404, 'Wishlist not found')
    @api.marshal_with(item_model)
    def get(self, wishlist_id):
        """ Returns all of the items in a Wishlist """
        app.logger.info("Request for items in the wishlist with id %s...", wishlist_id)
        wishlist = Wishlist.find_or_404(wishlist_id)
        results = [item.serialize() for item in wishlist.items]
        return results, status.HTTP_200_OK

    ######################################################################
    # ADD ITEMS TO AN EXISTING WISHLIST
    ######################################################################
    @api.doc('Add_items_to_an_existing_wishlist')
    @api.expect(create_item_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(404, 'Wishlist not found')
    @api.response(201, 'Add item to wishlist successfully')
    @api.marshal_with(item_model, code=201)
    def post(self, wishlist_id):
        """
        Adds items to a Wishlist
        This endpoint will add items to the Wishlist (id in path param)
        based the data in the posted body
        """
        app.logger.info("Request to add items to a wishlist")
        check_content_type("application/json")
        new_item = Item()
        app.logger.debug('Payload = %s', api.payload)
        new_item.deserialize(api.payload)

        if new_item.wishlist_id != wishlist_id:
            raise DataValidationError("wishlist_id in Item '{}' does not match "
                                    "wishlist_id in the url {}"
                                    .format(new_item.wishlist_id, wishlist_id))

        wishlist = Wishlist.find_or_404(wishlist_id)
        wishlist.items.append(new_item)

        wishlist.save()
        message = new_item.serialize()
        location_url = api.url_for(ItemResource,
                                wishlist_id=wishlist.id,
                                item_id=new_item.id,
                                _external=True)
        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /wishlists/<wishlist_id>/items/<item_id>
######################################################################
@api.route('/wishlists/<int:wishlist_id>/items/<int:item_id>', strict_slashes=False)
# @api.doc(params={'wishlist_id': 'The wishlist identifier', 'item_id': 'The wishlist item identifier'})
@api.param('wishlist_id', 'The wishlist identifier')
@api.param('item_id', 'The wishlist item identifier')
class ItemResource(Resource):
    """
    ItemResource class
    Allows the following operation on an item
    GET - Returns an Item with the Wishlist id and Item id
    DELETE -  Delete an Item with the Wishlist id and Item id
    """
    ######################################################################
    # GET ITEM FROM A WISHLIST
    ######################################################################
    @api.doc('get_item_from_wishlist')
    @api.response(404,'Item or wishlist not found')
    # @api.marshal_with(item_model)
    def get(self, wishlist_id, item_id):
        """
        Gets an item from a Wishlist
        This endpoint will return an Item based on it's id
        """
        app.logger.info("Request to get an item from a wishlist")

        wishlist = Wishlist.find_or_404(wishlist_id)

        get_item = None

        for item in wishlist.items:
            if item.id == item_id:
                get_item = item
                break

        if get_item is None:
            api.abort(status.HTTP_404_NOT_FOUND, "Item with id '{}' was not found.".format(item_id))

        message = get_item.serialize()
        return message, status.HTTP_200_OK


    ######################################################################
    # DELETE ITEM FROM A WISHLIST
    ######################################################################
    @api.doc('delete_item_from_wishlist')
    @api.response(204,'Item has been deleted')
    def delete(self, wishlist_id, item_id):
        """
        Deletes an item from a Wishlist
        This endpoint will return an Item based on its id
        """
        app.logger.info("Request to delete an item from a wishlist")
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            get_item = None
            for item in wishlist.items:
                if item.id == item_id:
                    get_item = item
                    break

            if get_item:
                get_item.delete()

        app.logger.info("Item with ID [%s] was deleted.", item_id)
        return '', status.HTTP_204_NO_CONTENT


######################################################################
# PATH: /wishlists/{wishlist_id}/enabled
######################################################################
@api.route('/wishlists/<int:wishlist_id>/enabled', strict_slashes=False)
@api.param('wishlist_id', 'The Wishlist identifier')
class EnableResource(Resource):
    """ Enable actions on a Wishlist """
    @api.doc('enable_wishlists')
    @api.response(404, 'Wishlist not found')
    def put(self, wishlist_id):
        """
        Enable a Wishlist
        This endpoint will enable a Wishlist based the id specified in the path
        """
        app.logger.info("Request to enable wishlist with id: %s", wishlist_id)
        wishlist = Wishlist.find_or_404(wishlist_id)
        wishlist.id = wishlist_id
        wishlist.status = True
        wishlist.save()
        message = wishlist.serialize()
        app.logger.info("Wishlist with ID [%s] enabled.", wishlist_id)
        return message, status.HTTP_200_OK


######################################################################
# PATH: /wishlists/{wishlist_id}/disabled
######################################################################
@api.route('/wishlists/<int:wishlist_id>/disabled', strict_slashes=False)
@api.param('wishlist_id', 'The Wishlist identifier')
class DisableResource(Resource):
    """ Disable actions on a Wishlist """
    @api.doc('disable_wishlists')
    @api.response(404, 'Wishlist not found')
    def put(self, wishlist_id):
        """
        Disable a Wishlist
        This endpoint will disable a Wishlist based the id specified in the path
        """
        app.logger.info("Request to disable wishlist with id: %s", wishlist_id)
        wishlist = Wishlist.find_or_404(wishlist_id)
        wishlist.id = wishlist_id
        wishlist.status = False
        wishlist.save()
        message = wishlist.serialize()
        app.logger.info("Wishlist with ID [%s] disabled.", wishlist_id)
        return message, status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Wishlist.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    abort(415, "Content-Type must be {}".format(content_type))
