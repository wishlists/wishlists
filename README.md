# Introduction
The wishlists resource allow customers to create a collection of products that they wish they had the money to purchase. A customer might have multiple wish lists so they might want to name them for easy identification. 

# Prerequisite Installation using Vagrant VM
The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download VirtualBox

Download Vagrant

Then all you have to do is clone this repo and invoke vagrant:

    git clone https://github.com/wishlists/wishlists
    cd wishlists
    vagrant up
    vagrant ssh
    cd /vagrant
    FLASK_APP=service:app flask run -h 0.0.0.0
    
You must pass the parameters -h 0.0.0.0 to have it listed on all network adapters to that the post can be forwarded by vagrant to your host computer so that you can open the web page in a local browser at: http://localhost:5000/wishlists

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

## Checking pep8 compliance

```shell
    $ flake8 --count --max-complexity=10 --statistics model,service
```