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
from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from flask_api import status  # HTTP Status Codes
from service.models import db, Wishlist
from service.service import app, init_db
from .wishlist_factory import WishlistFactory

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)


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
                "/wishlists", json=test_wishlist.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test wishlist"
            )
            new_wishlist = resp.get_json()
            test_wishlist.id = new_wishlist["id"]
            wishlists.append(test_wishlist)
        return wishlists

    def test_create_wishlist(self):
        """ Create a new wishlist """
        test_wishlist = WishlistFactory()
        resp = self.app.post(
            "/wishlists", json=test_wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], test_wishlist.name, "Names do not match")
        self.assertEqual(
            new_wishlist["user_id"], test_wishlist.user_id, "User id do not match"
        )
        # Check that the location header was correct
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], test_wishlist.name, "Names do not match")
        self.assertEqual(
            new_wishlist["user_id"], test_wishlist.user_id, "User id do not match"
        )

    def test_get_wishlist(self):
        """ Get a single wishlist """
        # get the id of a wishlist
        test_wishlist = self._create_wishlists(1)[0]
        resp = self.app.get(
            "/wishlists/{}".format(test_wishlist.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_wishlist.name)

    def test_get_wishlist_not_found(self):
        """ Get a wishlist thats not found """
        resp = self.app.get("/wishlists/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_create_wishlist_with_missing_args(self):
        test_wishlist = {
            "name":"wishlist1",
            "user_id":1
            }
        resp = self.app.post(
            "/wishlists", json=test_wishlist, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlist_with_unsupported_media_type(self):
        test_wishlist = {
            "name":"wishlist1",
            "user_id":1,
            "items":[]
            }
        resp = self.app.post(
            "/wishlists", json=test_wishlist, content_type="application/javascript"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        



######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
