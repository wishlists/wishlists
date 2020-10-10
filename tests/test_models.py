# Created by gupta at 10-10-2020

import unittest
import logging
import os
from service.models import Item, Wishlist, db, DataValidationError
from service import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  M O D E L   T E S T   C A S E S
######################################################################


class TestModel(unittest.TestCase):
    """
    Test case for Items model
    """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Item.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

######################################################################
#  T E S T   C A S E S
######################################################################

    def test_serialize_an_item(self):
        """Test Serialize an Item """
        item = Item(product_name='laptop', product_id=1, wishlist_id=1)
        data = item.serialize()

        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], None)
        self.assertIn("product_name", data)
        self.assertEqual(data["product_name"], "laptop")
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], 1)
        self.assertIn("wishlist_id", data)
        self.assertEqual(data["wishlist_id"], 1)

    def test_deserialize_a_item(self):
        """ Test deserialization of an Item """
        data = {"id": 1, "product_name": "laptop", "product_id": 1, "wishlist_id": 1}
        item = Item()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertNotEqual(data, None)
        self.assertEqual(item.id, None)
        self.assertEqual(item.product_name, data["product_name"])
        self.assertEqual(item.product_id, data["product_id"])
        self.assertEqual(item.wishlist_id, data["wishlist_id"])

    def test_item_deserialize_type_error(self):
        """ Test deserialization of type error for Item"""
        data = "this is not a dictionary"
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_item_deserialize_address_key_error(self):
        """ Deserialize an item with a KeyError for Item"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_serialize_a_wishlist(self):
        """ Serialize a wishlist """
        item = Item(product_name='laptop', product_id=1, wishlist_id=1)
        wishlist_obj = Wishlist(name="electronics", user_id=123, items=[item])

        wishlist = wishlist_obj.serialize()
        self.assertNotEqual(item, None)
        self.assertNotEqual(wishlist_obj, None)
        self.assertEqual(wishlist['id'], None)
        self.assertEqual(wishlist['name'], wishlist_obj.name)
        self.assertEqual(wishlist['user_id'], wishlist_obj.user_id)
        items = wishlist['items']
        self.assertEqual(items[0]['id'], None)
        self.assertEqual(items[0]['product_name'], item.product_name)
        self.assertEqual(items[0]['wishlist_id'], item.wishlist_id)
        self.assertEqual(items[0]['product_id'], item.product_id)

    def test_deserialize_a_wishlist(self):
        """ Deserialize a wishlist """
        item = Item(product_name='laptop', product_id=1, wishlist_id=1)
        wishlist_obj = Wishlist(name="electronics", user_id=123, items=[item])
        serial_wishlist = wishlist_obj.serialize()

        new_wishlist = Wishlist()
        new_wishlist.deserialize(serial_wishlist)
        self.assertEqual(new_wishlist.id, None)
        self.assertEqual(new_wishlist.name, wishlist_obj.name)
        self.assertEqual(new_wishlist.user_id, wishlist_obj.user_id)

    def test_wishlist_deserialize_type_error(self):
        """ Test deserialization of type error for Wishlist"""
        data = "this is not a dictionary"
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_wishlist_deserialize_address_key_error(self):
        """ Deserialize an item with a KeyError for Wishlist"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, {})

    def test_item_str(self):
        """ Test Item __str__ method"""
        item = Item(product_name='laptop', product_id=1, wishlist_id=1)
        self.assertEqual(str(item), 'laptop: product_id: 1, item_id: None, wishlist_id: 1')

    def test_wishlist_str(self):
        """ Test Wishlist __str__ method"""
        item = Item(product_name='laptop', product_id=1, wishlist_id=1)
        wishlist_obj = Wishlist(name="electronics", user_id=123, items=[item])
        self.assertEqual(str(wishlist_obj), 'electronics: id: None, user_id: 123, items: [<Item \'laptop\' id=[None] '
                                            'wishlist_id[1] product_id[1]>]')
