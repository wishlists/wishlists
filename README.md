# Introduction
The wishlists resource allows customers to create a collection of products that they wish they had the money to purchase. A customer might have multiple wishlists so they might want to name them for easy identification. 

## Prerequisite Installation using Vagrant VM
The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have these software, then the first step is to download and install them.

Download VirtualBox

Download Vagrant

Then all you have to do is to clone this repo and invoke vagrant:

    git clone https://github.com/wishlists/wishlists
    cd wishlists
    vagrant up
    vagrant ssh
    cd /vagrant
    FLASK_APP=service:app flask run -h 0.0.0.0
    
## Features supported

 GET /wishlists - Return all the wishlists
 
 GET /wishlists/{wishlist_id} - Return the wishlists with the given id  
 
 POST /wishlists - Create a new wishlist record in the database  

 PUT /wishlists/{wishlist_id} - Update a wishlist record in the database  
 
 DELETE /wishlists/{wishlist_id} - Delete a wishlist record in the database  
 
 GET /wishlists?name=wishlist_1 - Query the database by the name of the wishlist

 GET /wishlists?user_id=1 - Query the database by the user id of the wishlist

 PUT /wishlists/{wishlist_id}/disabled - It disables the target wishlist
 
 PUT /wishlists/{wishlist_id}/enabled - It enables the target wishlist
 
 POST /wishlists/{wishlist_id}/items - Add item into target wishlist

 GET /wishlists/{wishlist_id}/items/{item_id} - Get item by its id from target wishlist
 
 PUT /wishlists/{wishlist_id} - Updates an existing wishlist
 
 DELETE /wishlists/{wishlist_id}/items/{item_id} - Delete item by its id from target wishlist

 ## Manually running the Tests

Run the tests using `nose`

```shell
    $ nosetests
```

Nose is configured via the included `setup.cfg` file to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

Nose is also configured to automatically run the `coverage` tool and you should see a percentage of coverage report at the end of your tests. If you want to see what lines of code were not tested use:

```shell
    $ coverage report -m
```

This is particularly useful because it reports the line numbers for the code that is not covered so that you can write more test cases to get higher code coverage.

You can also manually run `nosetests` with `coverage` (but `setup.cfg` does this already)

```shell
    $ nosetests --with-coverage --cover-package=service
```

## Running Pylint to check PEP8

    vagrant up
    vagrant ssh
    cd /vagrant
    pylint --rcfile=pylint.conf service/*.py
    pylint --rcfile=pylint.conf tests/*.py
