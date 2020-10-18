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
GET /wishlists - Returns a list all of the wishlists
GET /wishlists/{id} - Returns the wishlist with a given id number
POST /wishlists - creates a new wishlist record in the database
PUT /wishlists/{id} - updates a wishlist record in the database
DELETE /wishlists/{id} - deletes a wishlist record in the database
"""

from flask import jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from service.models import Wishlist, Item, DataValidationError

# Import Flask application
from . import app


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
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Wishlist Demo REST API Service",
            version="1.0",
            paths=url_for("list_wishlists", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# LIST ALL WISHLISTS
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """ Returns all of the Wishlists """
    app.logger.info("Request for wishlist list")
    wishlists = []
    user_id = request.args.get("user_id")
    name = request.args.get("name")
    if user_id:
        try:
            user_id = int(user_id)
        except ValueError:
            abort(400, "The user_id should be an integer")
        wishlists = Wishlist.find_by_user_id(user_id)
    elif name:
        try:
            name = str(name)
        except ValueError:
            abort(400, "The name should be a string")
        wishlists = Wishlist.find_by_name(name)
    else:
        wishlists = Wishlist.all()

    results = [wishlist.serialize() for wishlist in wishlists]
    app.logger.info("Returning %d wishlists", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlists(wishlist_id):
    """
    Retrieve a single Wishlist
    This endpoint will return a Wishlist based on it's id
    """
    app.logger.info("Request for wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find_or_404(wishlist_id)
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A NEW WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Creates a Wishlist
    This endpoint will create a Wishlist based the data in the posted body
    """
    app.logger.info("Request to create a wishlist")
    check_content_type("application/json")
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()
    message = wishlist.serialize()
    location_url = url_for("get_wishlists",
                           wishlist_id=wishlist.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# ADD ITEMS TO AN EXISTING WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["POST"])
def add_items_to_wishlist(wishlist_id):
    """
    Adds items to a Wishlist
    This endpoint will add items to the Wishlist (id in path param)
    based the data in the posted body
    """
    app.logger.info("Request to add items to a wishlist")
    check_content_type("application/json")

    new_item = Item()
    new_item.deserialize(request.get_json())

    if new_item.wishlist_id != wishlist_id:
        raise DataValidationError("wishlist_id in Item '{}' does not match "
                                  "wishlist_id in the url {}"
                                  .format(new_item.wishlist_id, wishlist_id))

    wishlist = Wishlist.find_or_404(wishlist_id)
    wishlist.items.append(new_item)

    wishlist.save()
    message = new_item.serialize()
    location_url = url_for("get_item_from_wishlist",
                           wishlist_id=wishlist.id,
                           item_id=new_item.id,
                           _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# GET ITEM FROM A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["GET"])
def get_item_from_wishlist(wishlist_id, item_id):
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
        raise NotFound("Item with id '{}' was not found.".format(item_id))

    message = get_item.serialize()
    return make_response(jsonify(message), status.HTTP_200_OK)

######################################################################
# LIST ITEMS FROM WISHLISTS
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["GET"])
def list_items_in_wishlist(wishlist_id):
    """ Returns all of the items for a wishlist """
    app.logger.info("Request for items in the wishlist...")
    wishlist = Wishlist.find_or_404(wishlist_id)
    results = [item.serialize() for item in wishlist.items]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete a Wishlist
    This endpoint will delete a Wishlist based the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()

    app.logger.info("Wishlist with ID [%s] delete complete.", wishlist_id)
    return make_response("", status.HTTP_204_NO_CONTENT)


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
