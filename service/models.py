# Copyright 2016, 2019 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for Wishlists Service

All of the models are stored in this module

Models
------


Attributes:
-----------


"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Item(db.Model):
    """
    This class represents an item
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'),
                            nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(63), nullable=False)

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    def __repr__(self):
        return "<Item %r id=[%s] wishlist_id[%s] product_id[%s]>" % \
               (self.product_name, self.id, self.wishlist_id, self.product_id)

    def __str__(self):
        return "%s: product_id: %s, item_id: %s, wishlist_id: %s" % (
            self.product_name, self.product_id, self.id, self.wishlist_id)

    def serialize(self):
        """ Serializes an Item into a dictionary """
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "product_id": self.product_id,
            "product_name": self.product_name
        }

    def deserialize(self, data):
        """
        Deserializes an Item from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wishlist_id = data["wishlist_id"]
            self.product_id = data["product_id"]
            self.product_name = data["product_name"]
        except KeyError as error:
            raise DataValidationError("Invalid Item: missing " + error.args[0])
        except TypeError:
            raise DataValidationError(
                "Invalid Item: body of request contained" "bad or no data"
            )
        return self


class Wishlist(db.Model):
    """
    Class that represents a Wishlist

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    logger = logging.getLogger(__name__)
    app = None

    def __repr__(self):
        return "<Wishlist %r user_id=[%s] items[%s]>" % \
               (self.name, self.user_id, self.items)

    def __str__(self):
        return "%s: id: %s, user_id: %s, items: %s" % (
            self.name, self.id, self.user_id, str(self.items))

    ##################################################
    # Table Schema
    ##################################################

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    items = db.relationship('Item', backref='account', lazy=True)

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    def serialize(self):
        """ Serializes a Pet into a dictionary """
        wishlist = {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "items": []
        }

        for item in self.items:
            wishlist['items'].append(item.serialize())

        return wishlist

    def deserialize(self, data: dict):
        """
        Deserializes a Pet from a dictionary

        :param data: a dictionary of attributes
        :type data: dict

        :return: a reference to self
        :rtype: Pet

        """
        try:
            self.name = data["name"]
            self.user_id = data["user_id"]
            item_list = data.get("items")
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError("Invalid Wishlist: missing " +
                                      error.args[0])
        except TypeError:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data"
            )
        return self
