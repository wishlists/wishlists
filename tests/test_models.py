# Created by gupta at 10-10-2020

import unittest
import logging
import os
from service.models import Item, Wishlist, db, DataValidationError
from service import app
from tests.factories import WishlistFactory, ItemFactory

DATABASE_URI = os.getenv("DATABASE_URI",
                         "postgres://postgres:postgres@localhost:5432/testdb")


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
#  H E L P E R   M E T H O D S
######################################################################
    def _create_wishlist(self, items=[]):
        """ Creates an account from a Factory """
        fake_wishlist = WishlistFactory()
        wishlist = Wishlist(
            name=fake_wishlist.name,
            user_id=fake_wishlist.user_id,
            items=items,
            status=fake_wishlist.status
        )
        self.assertTrue(wishlist is not None)
        self.assertEqual(wishlist.id, None)
        return wishlist

    def _create_item(self):
        """ Creates fake items from factory """
        fake_item = ItemFactory()
        item = Item(
            wishlist_id=fake_item.wishlist_id,
            product_name=fake_item.product_name,
            product_id=fake_item.product_id
        )
        self.assertTrue(item is not None)
        self.assertEqual(item.id, None)
        return item


######################################################################
#  T E S T   C A S E S
######################################################################
    def test_create_a_wishlist(self):
        """ Create a wishlist and assert that it exists """
        fake_wishlist = WishlistFactory()
        wishlist = Wishlist(
            name=fake_wishlist.name,
            user_id=fake_wishlist.user_id,
            status=fake_wishlist.status
        )
        self.assertTrue(wishlist is not None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, fake_wishlist.name)
        self.assertEqual(wishlist.user_id, fake_wishlist.user_id)
        self.assertEqual(wishlist.status, fake_wishlist.status)

    def test_add_a_wishlist(self):
        """ Create a wishlist and add it to the database """
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = self._create_wishlist()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(wishlist.id, 1)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

    def test_update_wishlist(self):
        """ Update a wishlist """
        wishlist = self._create_wishlist()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(wishlist.id, 1)

        # Fetch it back
        wishlist = Wishlist.find_or_404(wishlist.id)
        wishlist.name = "new_name"
        wishlist.save()

        # Fetch it back again
        wishlist = Wishlist.find_or_404(wishlist.id)
        self.assertEqual(wishlist.name, "new_name")

    def test_add_wishlist_item(self):
        """ Create a wishlist with an item and add it to the database """
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = self._create_wishlist()
        item = self._create_item()
        wishlist.items.append(item)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(wishlist.id, 1)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        self.assertEqual(wishlist.items[0].product_name, item.product_name)

        item2 = self._create_item()
        wishlist.items.append(item2)
        wishlist.save()

        self.assertEqual(len(wishlist.items), 2)
        self.assertEqual(wishlist.items[1].product_name, item2.product_name)

    def test_find_or_404(self):
        """ Find or throw 404 error """
        wishlist = self._create_wishlist()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(wishlist.id, 1)

        # Fetch it back
        wishlist = Wishlist.find_or_404(wishlist.id)
        self.assertEqual(wishlist.id, 1)

    def test_find_by_name(self):
        """ Find by name """
        wishlist = self._create_wishlist()
        wishlist.create()

        # Fetch it back by name
        same_wishlist = Wishlist.find_by_name(wishlist.name)[0]
        self.assertEqual(same_wishlist.id, wishlist.id)
        self.assertEqual(same_wishlist.name, wishlist.name) 

    def test_find_by_user_id(self):
        """ Find by user id"""
        wishlist = self._create_wishlist()
        wishlist.create()

        # Fetch it back by user id
        same_wishlist = Wishlist.find_by_user_id(wishlist.user_id)[0]
        self.assertEqual(same_wishlist.id, wishlist.id)
        self.assertEqual(same_wishlist.user_id, wishlist.user_id)

    def test_delete_a_wishlist(self):
        """ Delete a Wishlist """
        item = Item(product_name='laptop', product_id=1, wishlist_id=1)
        wishlist_obj = Wishlist(name="electronics", user_id=123, items=[item])
        wishlist_obj.create()
        wishlist = Wishlist.find(wishlist_id=1)
        self.assertNotEqual(wishlist, None)
        # delete the wishlist and make sure it isn't in the database
        wishlist_obj.delete()
        wishlist = Wishlist.find(wishlist_id=1)
        self.assertEqual(wishlist, None)

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
        data = {"id": 1, "product_name": "laptop",
                "product_id": 1, "wishlist_id": 1}
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
        wishlist_obj = Wishlist(name="electronics", user_id=123, items=[item], status=True)

        wishlist = wishlist_obj.serialize()
        self.assertNotEqual(item, None)
        self.assertNotEqual(wishlist_obj, None)
        self.assertEqual(wishlist['id'], None)
        self.assertEqual(wishlist['name'], wishlist_obj.name)
        self.assertEqual(wishlist['user_id'], wishlist_obj.user_id)
        self.assertEqual(wishlist['status'], wishlist_obj.status)
        items = wishlist['items']
        self.assertEqual(items[0]['id'], None)
        self.assertEqual(items[0]['product_name'], item.product_name)
        self.assertEqual(items[0]['wishlist_id'], item.wishlist_id)
        self.assertEqual(items[0]['product_id'], item.product_id)

    def test_deserialize_a_wishlist(self):
        """ Deserialize a wishlist """
        item = Item(product_name='laptop', product_id=1, wishlist_id=1)
        wishlist_obj = Wishlist(name="electronics", user_id=123, items=[item], status=True)
        serial_wishlist = wishlist_obj.serialize()

        new_wishlist = Wishlist()
        new_wishlist.deserialize(serial_wishlist)
        self.assertEqual(new_wishlist.id, None)
        self.assertEqual(new_wishlist.name, wishlist_obj.name)
        self.assertEqual(new_wishlist.user_id, wishlist_obj.user_id)
        self.assertEqual(new_wishlist.status, wishlist_obj.status)

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
        self.assertEqual(str(item),
                         'laptop: product_id: 1, item_id: None, '
                         'wishlist_id: 1')

    def test_wishlist_str(self):
        """ Test Wishlist __str__ method"""
        item = Item(product_name='laptop', product_id=1, wishlist_id=1)
        wishlist_obj = Wishlist(name="electronics", user_id=123, items=[item], status=True)
        self.assertEqual(str(wishlist_obj),
                         'electronics: id: None, user_id: 123, items: '
                         '[<Item \'laptop\' id=[None] wishlist_id[1] '
                         'product_id[1]>], status: True')

    def test_wishlist_repr(self):
        """ Test Wishlist __repr__ method"""
        item = Item(product_name='laptop', product_id=1, wishlist_id=1)
        wishlist_obj = Wishlist(name="electronics", user_id=123, items=[item], status=True)
        print(repr(wishlist_obj))
        self.assertEqual(repr(wishlist_obj),
                         "<Wishlist 'electronics' user_id=[123] "
                         "items[[<Item 'laptop' id=[None] "
                         "wishlist_id[1] product_id[1]>]] status=[True]>")
