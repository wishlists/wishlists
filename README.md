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


