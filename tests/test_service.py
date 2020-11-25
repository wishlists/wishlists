# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
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
Wishlist API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import os
import logging
import unittest
from unittest.mock import patch
from flask import abort
from flask_api import status  # HTTP Status Codes
from service.models import db, DataValidationError
from service.service import app, init_db
from .factories import WishlistFactory, ItemFactory

DATABASE_URI = os.getenv("DATABASE_URI",
                         "postgres://postgres:postgres@localhost:5432/testdb")


######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistService(unittest.TestCase):
    """ Wishlist Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_wishlists(self, count):
        """ Factory method to create wishlists in bulk """
        wishlists = []
        for _ in range(count):
            test_wishlist = WishlistFactory()
            resp = self.app.post(
                "/wishlists",
                json=test_wishlist.serialize(),
                content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED,
                "Could not create test wishlist"
            )
            new_wishlist = resp.get_json()
            test_wishlist.id = new_wishlist["id"]
            wishlists.append(test_wishlist)
        return wishlists

    def _create_items(self, count=1, wishlist=None):
        """ Factory method to create items in bulk """
        items = []
        if wishlist is None:
            print("none")
            wishlist = self._create_wishlists(1)[0]

        for _ in range(count):
            test_item = ItemFactory()
            test_item.wishlist_id = wishlist.id

            resp = self.app.post(
                "/wishlists/{}/items".format(wishlist.id),
                json=test_item.serialize(), content_type="application/json"
            )

            self.assertEqual(resp.status_code, status.HTTP_201_CREATED,
                             "Could not create test wishlist")
            new_item = resp.get_json()
            test_item.id = new_item["id"]
            items.append(test_item)
        return wishlist, items

    def test_index(self):
        """ Test the Home UI Page for wishlist"""
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Wishlist RESTful Service", resp.data)

    def test_homepage(self):
        """ Test the Home UI Page for items"""
        resp = self.app.get('/items.html')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Wishlist RESTful Service (Items)", resp.data)

    def test_create_wishlist_bad_data(self):
        """Test create wishlist """

        test_wishlist = {"name": "abc",
                         "user_id": 123}

        resp = self.app.post(
            "/wishlists",
            json=test_wishlist,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertEqual(data["message"], "Invalid Wishlist: missing items")

    def test_create_wishlist(self):
        """ Create a new wishlist """
        test_wishlist = WishlistFactory()
        item = ItemFactory()
        test_wishlist.items.append(item)
        resp = self.app.post(
            "/wishlists",
            json=test_wishlist.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertTrue(location is not None)
        # Check the data is correct
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], test_wishlist.name,
                         "Names do not match")
        self.assertEqual(
            new_wishlist["user_id"], test_wishlist.user_id,
            "User id do not match"
        )
        items = new_wishlist["items"][0]
        self.assertEqual(items["product_name"]
                         , item.product_name,
                         "item product_name do not match"
                         )
        # Check that the location header was correct
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], test_wishlist.name,
                         "Names do not match")
        self.assertEqual(
            new_wishlist["user_id"], test_wishlist.user_id,
            "User id do not match"
        )

    def test_get_wishlist_list(self):
        """ Get a list of Wishlists """
        self._create_wishlists(10)
        resp = self.app.get("/wishlists")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 10)

    def test_get_wishlist_list_by_name(self):
        """ Get a list of Wishlists with the same name """
        wishlist = self._create_wishlists(1)[0]
        resp = self.app.get("/wishlists?name={}".format(wishlist.name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        same_wishlist = data[0]
        self.assertEqual(same_wishlist["name"], wishlist.name)

    def test_get_wishlist_list_by_user_id(self):
        """ Get a list of Wishlists with the same user id """
        wishlist = self._create_wishlists(1)[0]
        resp = self.app.get("/wishlists?user_id={}".format(wishlist.user_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        same_wishlist = data[0]
        self.assertEqual(same_wishlist["user_id"], wishlist.user_id)

    def test_get_wishlist_list_by_user_id_wrong_data_type(self):
        """ Query a list of wishlists using argument with wrong data type """
        resp = self.app.get("/wishlists?user_id=\"1\"")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_wishlist_list_by_nonexist_args(self):
        """ Query a list of wishlists using nonexist argument"""
        resp = self.app.get("/wishlists?length=20")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_wishlist(self):
        """ Get a single wishlist """
        # get the id of a wishlist
        test_wishlist = self._create_wishlists(1)[0]
        resp = self.app.get(
            "/wishlists/{}".format(test_wishlist.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_wishlist.name)

    def test_get_wishlist_not_found(self):
        """ Get a wishlist thats not found """
        resp = self.app.get("/wishlists/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertEqual(data['message'],
                         "Wishlist with id '0' was not found. " 
                         "You have requested this URI [/wishlists/0] "
                         "but did you mean /wishlists/<int:wishlist_id> "
                         "or /wishlists/500 or /wishlists ?")

    def test_create_wishlist_with_missing_args(self):
        """ Test the wishlist added has missing arguments """
        test_wishlist = {
            "name": "wishlist1"
        }
        resp = self.app.post(
            "/wishlists", json=test_wishlist, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertEqual(data['error'], "Bad Request")
        self.assertEqual(data['message'],
                         'Invalid Wishlist: missing user_id')

    def test_create_wishlist_with_unsupported_media_type(self):
        """ Test the wishlist add request with unsupported media type """
        test_wishlist = {
            "name": "wishlist1",
            "user_id": 1,
            "items": []
        }
        resp = self.app.post(
            "/wishlists", json=test_wishlist,
            content_type="application/javascript"
        )
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = resp.get_json()
        self.assertEqual(data['message'],
                         'Content-Type must be application/json')

    def test_add_item_to_wishlist(self):
        """ Add an item to an existing wishlist """
        test_wishlist = self._create_wishlists(1)[0]
        new_item = ItemFactory()
        new_item.wishlist_id = test_wishlist.id

        resp = self.app.post(
            "/wishlists/{}/items".format(test_wishlist.id),
            json=new_item.serialize(),
            content_type="application/json"
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertTrue(location is not None)
        # Check the data is correct
        resp_item = resp.get_json()

        self.assertEqual(resp_item["wishlist_id"], new_item.wishlist_id,
                         "Wishlist id does not match")
        self.assertEqual(resp_item["product_id"], new_item.product_id,
                         "Product id does not match")
        self.assertEqual(resp_item["product_name"], new_item.product_name,
                         "Product name does not match")

        # Check that the location header was correct
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        loc_resp_item = resp.get_json()
        self.assertEqual(loc_resp_item["id"], resp_item['id'],
                         "item id does not match")
        self.assertEqual(loc_resp_item["wishlist_id"], new_item.wishlist_id,
                         "Wishlist id does not match")
        self.assertEqual(loc_resp_item["product_id"], new_item.product_id,
                         "Product id does not match")
        self.assertEqual(loc_resp_item["product_name"], new_item.product_name,
                         "Product name does not match")

    def test_get_item_from_wishlist(self):
        """ Get a single wishlist """
        # get the id of a wishlist
        wishlist, items = self._create_items(1)
        item = items[0]
        resp = self.app.get(
            "/wishlists/{}/items/{}".format(wishlist.id, item.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["product_name"], item.product_name)

    def test_get_item_not_found(self):
        """ Test get_item if item is not found """

        wishlist = self._create_items(1)[0]
        resp = self.app.get(
            "/wishlists/{}/items/{}".format(wishlist.id, 55000),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertEqual(data["message"],
                         "404 Not Found: Item with id '{}' was not found."
                         .format(55000))

    def test_add_item_to_wishlist_unsupported_media_type(self):
        """ Test add item to a wishlist if unsupported media type """

        test_wishlist = self._create_wishlists(1)[0]

        new_item = ItemFactory()
        new_item.wishlist_id = test_wishlist.id

        resp = self.app.post(
            "/wishlists/{}/items".format(test_wishlist.id),
            json=new_item.serialize(),
            content_type="application/javascript"
        )

        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = resp.get_json()
        app_type = "application/json"
        self.assertEqual(data["message"],
                         "Content-Type must be {}"
                         .format(app_type))

    def test_add_item_to_wishlist_bad_request(self):
        """ Test add item to a wishlist if bad request """
        # get the id of a wishlist

        test_wishlist = self._create_wishlists(1)[0]

        new_item_json = {
            "product_name": "laptop",
            "wishlist_id": test_wishlist.id
        }

        resp = self.app.post(
            "/wishlists/{}/items".format(test_wishlist.id), json=new_item_json,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertEqual(data["message"], "Invalid Item: missing product_id")

    def test_add_item_to_wishlist_bad_request_2(self):
        """ Test add item to a wishlist if bad request
            for mismatch in wishlist_id"""

        test_wishlist, items = self._create_items()

        item = items[0]
        item.wishlist_id = 5

        resp = self.app.post(
            "/wishlists/{}/items".format(test_wishlist.id),
            json=item.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertEqual(data["message"], "wishlist_id in Item '{}' does not "
                                          "match wishlist_id in the url {}"
                         .format(item.wishlist_id,
                                 test_wishlist.id))

    @patch('service.service')
    def test_method_not_allowed(self, method_not_allowed_mock):
        """ Test a METHOD_NOT_ALLOWED error from Find By Name """
        method_not_allowed_mock.side_effect = DataValidationError()
        test_wishlist = WishlistFactory()
        resp = self.app.put(
            "/wishlists",
            json=test_wishlist.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_500_internal_server_error(self):
        """ Test 500_INTERNAL_SERVER_ERROR """

        @app.route('/wishlists/500')
        def internal_server_error():
            abort(500)

        resp = self.app.get('/wishlists/500')
        self.assertEqual(resp.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_delete_wishlist(self):
        """ Delete a non-existing Wishlist """
        test_wishlist = WishlistFactory()
        resp = self.app.delete(
            "/wishlists/{}".format(test_wishlist.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/wishlists/{}".format(test_wishlist.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_existing_wishlist(self):
        """ Delete an existing Wishlist """
        test_wishlist = self._create_wishlists(1)[0]
        resp = self.app.delete(
            "/wishlists/{}".format(test_wishlist.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/wishlists/{}".format(test_wishlist.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_items_from_wishlist(self):
        """ Get a list of Addresses """
        test_wishlist = self._create_wishlists(1)[0]
        # # create item 1
        new_item_1 = ItemFactory()
        new_item_1.wishlist_id = test_wishlist.id

        resp = self.app.post(
            "/wishlists/{}/items".format(test_wishlist.id),
            json=new_item_1.serialize(),
            content_type="application/json"
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # # create item 2
        new_item_2 = ItemFactory()
        new_item_2.wishlist_id = test_wishlist.id

        resp = self.app.post(
            "/wishlists/{}/items".format(test_wishlist.id),
            json=new_item_2.serialize(),
            content_type="application/json"
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.app.get(
            "/wishlists/{}/items".format(test_wishlist.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_get_items_from_nonexistent_wishlist(self):
        """ Get a wishlist thats not found """
        resp = self.app.get("/wishlists/0/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertEqual(data['message'],
                         "Wishlist '0' was not found. " 
                         "You have requested this URI [/wishlists/0/items] "
                         "but did you mean /wishlists/<int:wishlist_id>/items "
                         "or /wishlists/<int:wishlist_id> "
                         "or /wishlists/500 ?")

    def test_update_existing_wishlist(self):
        """ Update an existing Wishlist """
        # Create a wishlist to update
        test_wishlist = self._create_wishlists(1)[0]

        # Update the wishlist
        new_wishlist = test_wishlist
        new_wishlist.name = "devops"
        resp = self.app.put(
            "/wishlists/{}".format(test_wishlist.id),
            json=new_wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["name"], new_wishlist.name)

        resp = self.app.get(
            "/wishlists/{}".format(test_wishlist.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], new_wishlist.name)

    def test_update_non_existing_wishlist(self):
        """ Update a non-existing Wishlist """
        test_wishlist = WishlistFactory()
        # make sure they are not in database
        resp = self.app.get(
            "/wishlists/{}".format(test_wishlist.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        resp = self.app.put(
            "/wishlists/{}".format(test_wishlist.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_wishlist_list_with_missing_parameters(self):
        """ Update a Wishlist with missing parameters """
        # Create a wishlist to update
        test_wishlist = WishlistFactory()
        resp = self.app.post(
            "/wishlists", json=test_wishlist.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Update the wishlist
        new_wishlist = resp.get_json()
        missing_parameters_wishlist = {}
        resp = self.app.put(
            "/wishlists/{}".format(new_wishlist["id"]),
            json=missing_parameters_wishlist,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertEqual(data['error'], "Bad Request")
        self.assertEqual(data['message'],
                         'Invalid Wishlist: missing name')

    def test_update_wishlist_with_unsupported_media_type(self):
        """ Update a Wishlist with unsupported media type """
        test_wishlist = self._create_wishlists(1)[0]
        new_item = ItemFactory()
        new_item.wishlist_id = test_wishlist.id

        resp = self.app.put(
            "/wishlists/{}".format(test_wishlist.id),
            json=new_item.serialize(),
            content_type="application/javascript"
        )

        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = resp.get_json()
        app_type = "application/json"
        self.assertEqual(data["message"],
                        "Content-Type must be {}"
                        .format(app_type))

    def test_enable_existing_wishlist(self):
        """ Enable an existing Wishlist """
        test_wishlist = self._create_wishlists(1)[0]
        # disable the wishlist first because the default is enabled
        resp = self.app.put(
            "/wishlists/{}/disabled".format(test_wishlist.id),
            json=test_wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check that the status is correct
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["status"], False)

        # enable the wishlist
        resp = self.app.put(
            "/wishlists/{}/enabled".format(test_wishlist.id),
            json=test_wishlist.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check that the status is correct
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["status"], True)

    def test_enable_wishlist(self):
        """ Enable a non-existing Wishlist """
        test_wishlist = WishlistFactory()
        # enable the wishlist
        resp = self.app.put(
            "/wishlists/{}/enabled".format(test_wishlist.id),
            json=test_wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertEqual(data["message"],
                         "404 Not Found: Wishlist '{}' was not found."
                         .format(test_wishlist.id))

    def test_disable_existing_wishlist(self):
        """ Disable an existing Wishlist """
        test_wishlist = self._create_wishlists(1)[0]
        # disable the wishlist
        resp = self.app.put(
            "/wishlists/{}/disabled".format(test_wishlist.id),
            json=test_wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check that the status is correct
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["status"], False)

    def test_disable_wishlist(self):
        """ Disable a non-existing Wishlist """
        test_wishlist = WishlistFactory()
        # disable the wishlist
        resp = self.app.put(
            "/wishlists/{}/disabled".format(test_wishlist.id),
            json=test_wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertEqual(data["message"],
                         "404 Not Found: Wishlist '{}' was not found."
                         .format(test_wishlist.id))

    def test_delete_item_from_wishlist(self):
        """ Delete a single item """
        # create a wishlist with item
        wishlist, items = self._create_items(1)
        item = items[0]
        resp = self.app.delete(
            "/wishlists/{}/items/{}".format(wishlist.id, item.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # make sure it's deleted
        resp = self.app.get(
            "/wishlists/{}/items/{}".format(wishlist.id, item.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_if_wishlist_not_found(self):
        """ Test delete_item if wishlist is not found """
        wishlist = WishlistFactory()
        item = ItemFactory()
        resp = self.app.delete(
            "/wishlists/{}/items/{}".format(wishlist.id, item.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

    def test_delete_item_if_item_not_found(self):
        """ Test delete_item if item is not found """
        wishlist, _ = self._create_items(1)
        item = ItemFactory()
        resp = self.app.delete(
            "/wishlists/{}/items/{}".format(wishlist.id, item.id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

######################################################################
#   M A I N
######################################################################


if __name__ == "__main__":
    unittest.main()
