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


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase():
    """ Base class added persistent methods """

    def create(self):
        """
        Creates an Account to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a record to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Wishlist from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find(cls, wishlist_id: int):
        """Finds a Wishlist by it's ID
        :param wishlist_id: the id of the Wishlist to find
        :type wishlist_id: int
        :return: an instance with the wishlist_id, or None if not found
        :rtype: class object
        """
        cls.logger.info("Processing lookup for id %s ...", wishlist_id)
        return cls.query.get(wishlist_id)

    @classmethod
    def find_or_404(cls, by_id: int):
        """Finds a record by it's ID
        :param wishlist_id: the id of the record to find
        :type wishlist_id: int
        :return: an instance with the class, or None if not found
        :rtype: class object
        """
        cls.logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get_or_404(by_id, "{} '{}' was not found."
                                    .format(cls.__name__, by_id))

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the records in the database """
        cls.logger.info("Processing all Wishlists")
        return cls.query.all()


##################################################
# ITEM MODEL
##################################################
class Item(db.Model, PersistentBase):
    """ This class represents an item """

    logger = logging.getLogger(__name__)
    app = None

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'),
                            nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(63), nullable=False)

    def __repr__(self):
        return "<Item %r id=[%s] wishlist_id[%s] product_id[%s]>" % (
            self.product_name, self.id, self.wishlist_id, self.product_id)

    def __str__(self):
        return "%s: product_id: %s, item_id: %s, wishlist_id: %s" % (
            self.product_name, self.product_id, self.id, self.wishlist_id)

    ##################################################
    # INSTANCE METHODS
    ##################################################
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


##################################################
# WISHLIST MODEL
##################################################
class Wishlist(db.Model, PersistentBase):
    """
    Class that represents a Wishlist

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    logger = logging.getLogger(__name__)
    app = None

    def __repr__(self):
        return "<Wishlist %r user_id=[%s] items[%s]>" % (
            self.name, self.user_id, self.items)

    def __str__(self):
        return "%s: id: %s, user_id: %s, items: %s" % (
            self.name, self.id, self.user_id, str(self.items))

    ##################################################
    # Table Schema
    ##################################################

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    items = db.relationship('Item', backref='wishlist',
                            cascade="all,delete",
                            lazy=True)


    ##################################################
    # INSTANCE METHODS
    ##################################################
    def serialize(self):
        """ Serializes a Wishlist into a dictionary """
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
        Deserializes a Wishlist from a dictionary

        :param data: a dictionary of attributes
        :type data: dict

        :return: a reference to self
        :rtype: Wishlist

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
                "Invalid Wishlist: body of request contained bad or no data"
            )
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def find_by_name(cls, name: str):
        """Returns all Wishlists with the given name

        :param name: the name of the Wishlists you want to match
        :type name: str

        :return: a collection of Wishlists with that name
        :rtype: list

        """
        cls.logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_user_id(cls, user_id: int):
        """Returns all Wishlists with the given user id

        :param user_id: the user id of the Wishlists you want to match
        :type user_id: str

        :return: a collection of Wishlists with that user id
        :rtype: list

        """
        cls.logger.info("Processing user id query for %s ...", user_id)
        return cls.query.filter(cls.user_id == user_id)
