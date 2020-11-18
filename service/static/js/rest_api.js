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

    // Clears all Wishlist form fields
    function clear_wishlist_form_data() {
        $("#wishlist_name").val("");
        $("#wishlist_user_id").val("");
        $("#wishlist_items").val("");
        $("#wishlist_status").val("");
    }

    // Clears all Item form fields
    function clear_item_form_data() {
        $("#item_wishlist_id").val("");
        $("#item_product_id").val("");
        $("#item_product_name").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#create-btn").click(function () {

        var name = $("#wishlist_name").val();
        var user_id = $("#wishlist_user_id").val();
        var status = $("#wishlist_status").val() == "Enabled";

        var data = {
            "name": name,
            "user_id": user_id,
            "items": [],
            "status": status
        };
        
        var ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_wishlist_form_data(res)
            $("#search_results").empty();
            $("#search_results_items").empty();
            flash_message("Success")    
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve a Wishlist
    // ****************************************

    $("#retrieve-btn").click(function () {

        var wishlist_id = $("#wishlist_id").val();

        if(wishlist_id == null || wishlist_id.trim() === ""){
            alert("Please Enter Wishlist id");
            return ;
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/wishlists/" + wishlist_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_wishlist_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update the Wishlist from the form
    // ****************************************

    $("#update-btn").click(function () {
        var wishlist_id = $("#wishlist_id").val();
        var name = $("#wishlist_name").val();
        var user_id = $("#wishlist_user_id").val();
        var status = $("#wishlist_status").val();

        if(wishlist_id == null || wishlist_id.trim() === ""){
            alert("Please Enter Wishlist id");
            return ;
        }

        var data = {
            "name": name,
            "user_id": user_id
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/wishlists/" + wishlist_id,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            if ((res.status === true && status === "false") || (res.status === false && status === "true")) {
                if(status === "false"){
                    disableWishlist(wishlist_id);
                    res.status = false;
                } else {
                    enableWishlist(wishlist_id);
                    res.status = true;
                }
            }

            update_wishlist_form_data(res)
            $("#search_results").empty();
            $("#search_results_items").empty();
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update status of Wishlist
    // ****************************************

    // Enabled

    function enableWishlist(wishlist_id){
        var data = {};

        var ajax = $.ajax({
            type: "PUT",
            url: "/wishlists/" + wishlist_id + "/enabled",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(){
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    }

    // Disabled

    function disableWishlist(wishlist_id){
        var data = {};

        var ajax = $.ajax({
            type: "PUT",
            url: "/wishlists/" + wishlist_id + "/disabled",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(){
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    }

    // ****************************************
    // Delete a Wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        var wishlist_id = $("#wishlist_id").val();

        if(wishlist_id == null || wishlist_id.trim() === ""){
            alert("Please Enter Wishlist id");
            return ;
        }
       
        var ajax = $.ajax({
            type: "DELETE",
            url: "/wishlists/" + wishlist_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            clear_wishlist_form_data()
            $("#search_results").empty();
            $("#search_results_items").empty();
            flash_message("Wishlist has been deleted")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Add an item to a Wishlist
    // ****************************************

    $("#create-item-btn").click(function () {

        var wishlist_id = $("#item_wishlist_id").val();
        var product_id = $("#item_product_id").val();
        var product_name = $("#item_product_name").val();

        if(wishlist_id == null || wishlist_id.trim() === ""
            || product_id == null || product_id.trim() === ""
            || product_name == null || product_name.trim() === ""){
            alert("Wishlist ID, Product Name and Product ID are required fields");
            return ;
        }

        var data = {
            "wishlist_id": parseInt(wishlist_id),
            "product_id": product_id,
            "product_name": product_name
        };
        
        var ajax = $.ajax({
            type: "POST",
            url: "/wishlists/" + wishlist_id + "/items",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_item_form_data(res)

            $("#search_results").empty();

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Clear the Wishlist form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        clear_wishlist_form_data()
    });

    // ****************************************
    // Clear the Item form
    // ****************************************

    $("#clear-item-btn").click(function () {
        $("#item_id").val("");
        clear_item_form_data()
    });

    // ******************************************
    // Search for a Wishlist (list all wishlists)
    // ******************************************

    $("#search-btn").click(function () {

        var name = $("#wishlist_name").val();
        var user_id = $("#wishlist_user_id").val();

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

        if(queryString.length > 0)
            queryString = "?" + queryString;

        var ajax = $.ajax({
            type: "GET",
            url: "/wishlists" + queryString
        })

        ajax.done(function(res){

            $("#search_results").empty();
            $("#search_results").append('<h4>Wishlists</h4>');
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:20%">ID</th>'
            header += '<th style="width:20%">Name</th>'
            header += '<th style="width:20%">UserID</th>'
            header += '<th style="width:20%">Status</th></tr>'
            $("#search_results").append(header);
            var firstWishlist = "";
            var items = []

            for(var i = 0; i < res.length; i++) {
                var wishlist = res[i];
                var row = "<tr><td>"+wishlist.id+"</td><td>"+wishlist.name+"</td><td>"+ wishlist.user_id +"</td><td>" +
                    (wishlist.status ? "enabled" : "disabled") + "</td></tr>";

                $("#search_results").append(row);

                for(var j = 0; j < wishlist.items.length; j++){
                    items.push(wishlist.items[j]);
                }

                if (i === 0) {
                    firstWishlist = wishlist;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstWishlist != "") {
                update_wishlist_form_data(firstWishlist)
            }

            addItemsTable(items, "search_results_items")

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ***********************************************
    // Search for Wishlist Items (list wishlist items)
    // ***********************************************

    $("#search-item-btn").click(function () {

        var wishlist_id = $("#item_wishlist_id").val();

        var item_id = $("#item_id").val();

        if(wishlist_id == null || wishlist_id.trim() === ""){
            alert("Please Enter Wishlist id");
            return ;
        }

        var ajax = item_id == null || item_id.trim() === "" ? $.ajax({
            type: "GET",
            url: "/wishlists/" + wishlist_id + "/items"
        }) : $.ajax({
            type: "GET",
            url: "/wishlists/" + wishlist_id + "/items/" + item_id
        });


        ajax.done(function(res){

            addItemsTable(res, "search_results")

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    function addItemsTable(res, divID){

        $("#" + divID + "").empty();
        $("#search_results").append('<h4>Items</h4>');
        $("#" + divID + "").append('<table class="table-striped" cellpadding="10">');
        var header = '<tr>'
        header += '<th style="width:20%">ID</th>'
        header += '<th style="width:20%">Wishlist ID</th>'
        header += '<th style="width:20%">Product Name</th>'
        header += '<th style="width:20%">Product ID</th></tr>'
        $("#" + divID + "").append(header);
        var firstItem = "";

        // When a single item is returned
        if(!Array.isArray(res)){
            temp = [];
            temp.push(res);
            res = temp;
        }

        for(var i = 0; i < res.length; i++) {
            var item = res[i];
            var row = "<tr><td>"+item.id+"</td><td>"+ item.wishlist_id +"</td><td>"+item.product_name+"</td><td>"+ item.product_id +"</td></tr>";
            $("#" + divID + "").append(row);
            if (i === 0) {
                firstItem = item;
            }
        }

        $("#" + divID + "").append('</table>');

        // copy the first result to the form
        if (firstItem !== "") {
            update_item_form_data(firstItem)
        }
    }

})