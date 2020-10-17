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
from unittest.mock import MagicMock, patchfrom flask import abort
from flask_api import status  # HTTP Status Codes
from service.models import db
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
        pass

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
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Wishlist Demo REST API Service")

    def test_create_wishlist(self):
        """ Create a new wishlist """
        test_wishlist = WishlistFactory()
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
        resp = self.app.get("/wishlists?user_id=\"1\"")
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
        self.assertEqual(data['error'], "Not Found")
        self.assertEqual(data['message'], ("404 Not Found:"
                                           " Wishlist '0' was not found."))

    def test_create_wishlist_with_missing_args(self):
        test_wishlist = {
            "name": "wishlist1",
            "user_id": 1
        }
        resp = self.app.post(
            "/wishlists", json=test_wishlist, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertEqual(data['error'], "Bad Request")
        self.assertEqual(data['message'],
                         ('Invalid Wishlist:'
                          ' body of request contained bad or no data'))

    def test_create_wishlist_with_unsupported_media_type(self):
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
        self.assertEqual(data['error'], "Unsupported media type")
        self.assertEqual(data['message'],
                         ('415 Unsupported Media Type: Content-Type '
                          'must be application/json'))

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

        wishlist, items = self._create_items(1)
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
                         "415 Unsupported Media Type: Content-Type must be {}"
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

    @patch('service.service.Wishlist')
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

######################################################################
#   M A I N
######################################################################


if __name__ == "__main__":
    unittest.main()
