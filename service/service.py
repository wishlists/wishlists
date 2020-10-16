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
from service.models import Wishlist, Item

# Import Flask application
from . import app


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
    This endpoint will add items to the Wishlist (id in path param) based the data in the posted body
    """
    app.logger.info("Request to add items to a wishlist")
    check_content_type("application/json")

    wishlist = Wishlist.find_or_404(wishlist_id)
    new_item = Item()
    new_item.deserialize(request.get_json())

    wishlist.items.append(new_item)

    wishlist.save()
    message = new_item.serialize()
    location_url = url_for("get_item_from_wishlist",
                           wishlist_id=wishlist.id, item_id=new_item.id, _external=True)
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
