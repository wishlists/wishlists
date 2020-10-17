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
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import logging
from flask import Flask

# Create Flask application
app = Flask(__name__)
app.config.from_object('config')

# Import the rutes After the Flask app is created
from service import service

# Set up logging for production
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.propagate = False
    # Make all log formats consistent
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] \
    [%(module)s] %(message)s", "%Y-%m-%d %H:%M:%S %z")
    for handler in app.logger.handlers:
        handler.setFormatter(formatter)
    app.logger.info('Logging handler established')

app.logger.info(70 * "*")
app.logger.info("  WISHLISTS  ".center(70, "*"))
app.logger.info(70 * "*")

service.init_db()  # make our sqlalchemy tables

app.logger.info("Service initialized!")
