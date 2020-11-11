$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the Wishlist form with data from the response
    function update_wishlist_form_data(res) {
        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.name);
        $("#wishlist_user_id").val(res.user_id);
        $("#wishlist_items").val(res.items);
        if (res.status == true) {
            $("#wishlist_status").val("true");
        } else {
            $("#wishlist_status").val("false");
        }
    }

    // Updates the Item form with data from the response
    function update_item_form_data(res) {
        $("#item_id").val(res.id);
        $("#item_wishlist_id").val(res.wishlist_id);
        $("#item_product_id").val(res.product_id);
        $("#item_product_name").val(res.product_name);
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Search for a Wishlist (list all wishlists)
    // ****************************************

    $("#search-btn").click(function () {

        var name = $("#wishlist_name").val();
        var user_id = $("#wishlist_user_id").val();
        var items = $("#wishlist_items").val();
        var status = $("#wishlist_status").val() == "true";

        var queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (user_id) {
            if (queryString.length > 0) {
                queryString += '&user_id=' + user_id
            } else {
                queryString += 'user_id=' + user_id
            }
        }
        if (items) {
            if (queryString.length > 0) {
                queryString += '&items=' + items
            } else {
                queryString += 'items=' + items
            }
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/wishlists?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:20%">ID</th>'
            header += '<th style="width:20%">Name</th>'
            header += '<th style="width:20%">UserID</th>'
            header += '<th style="width:20%">Items</th>'
            header += '<th style="width:20%">Status</th></tr>'
            $("#search_results").append(header);
            var firstWishlist = "";
            for(var i = 0; i < res.length; i++) {
                var wishlist = res[i];
                var row = "<tr><td>"+wishlist.id+"</td><td>"+wishlist.name+"</td><td>"+wishlist.user_id+"</td><td>"+wishlist.items+"</td><td>"+wishlist.status+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstWishlist = wishlist;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstWishlist != "") {
                update_wishlist_form_data(firstWishlist)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Search for an Item (list all items)
    // ****************************************

    $("#search-item-btn").click(function () {
        
        $("#item_id").val(res.id);
        $("#item_wishlist_id").val(res.wishlist_id);
        $("#item_product_id").val(res.product_id);
        $("#item_product_name").val(res.product_name);


        var wishlist_id = $("#item_wishlist_id").val();
        var product_id = $("#item_product_id").val();
        var product_name = $("#item_product_name").val();

        var queryString = ""

        if (wishlist_id) {
            queryString += 'wishlist_id=' + wishlist_id
        }
        if (product_id) {
            if (queryString.length > 0) {
                queryString += '&product_id=' + product_id
            } else {
                queryString += 'product_id=' + product_id
            }
        }
        if (product_name) {
            if (queryString.length > 0) {
                queryString += '&product_name=' + product_name
            } else {
                queryString += 'product_name=' + product_name
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/pets?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:40%">Name</th>'
            header += '<th style="width:40%">Category</th>'
            header += '<th style="width:10%">Available</th></tr>'
            $("#search_results").append(header);
            var firstPet = "";
            for(var i = 0; i < res.length; i++) {
                var pet = res[i];
                var row = "<tr><td>"+pet._id+"</td><td>"+pet.name+"</td><td>"+pet.category+"</td><td>"+pet.available+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstPet = pet;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstPet != "") {
                update_item_form_data(firstPet)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})