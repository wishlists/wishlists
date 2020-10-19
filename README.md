# Introduction
The wishlists resource allow customers to create a collection of products that they wish they had the money to purchase. A customer might have multiple wishlists so they might want to name them for easy identification. 

## Prerequisite Installation using Vagrant VM
The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download VirtualBox

Download Vagrant

Then all you have to do is clone this repo and invoke vagrant:

    git clone https://github.com/wishlists/wishlists
    cd wishlists
    vagrant up
    vagrant provision
    vagrant ssh
    cd /vagrant
    FLASK_APP=service:app flask run -h 0.0.0.0
    
## Features supported

 GET /wishlists - Return all the wishlists 
 
 GET /wishlists/{wishlistID} - Return the wishlists with the given id  
 
 POST /wishlists - Create a new wishlist record in the database  

 PUT /wishlists/{wishlistID} - Update a wishlist record in the database  
 
 DELETE /wishlists/{wishlistID} - Delete a wishlist record in the database  
 
 GET /wishlists?name="wishlist_1" - Query the database by the name of the wishlist   

 PUT /wishlists/{wishlistId}/disabled - It disables the target wishlist
 
 PUT /wishlists/{wishlistId}/enabled - It enables the target wishlist
 
 POST /wishlists/{wishlistId}/items - Add item into target wishlist

 GET /wishlists/{wishlistId}/items/{item_id} - Get item by id from target wishlist 
 
 PUT /wishlists/{wishlist_id} - Updates an existing wishlist
 
 PUT /wishlists/{wishlist_id}/items/{item_id} - Updates an existing item in the target wishlist
 
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
```
vagrant up
vagrant ssh
cd /vagrant
pylint --rcfile=pylint.conf service/*.py
pylint --rcfile=pylint.conf tests/*.py
