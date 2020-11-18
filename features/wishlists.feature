Feature: The wishlist service back-end
    As a Wishlist Service Developer
    I need a RESTful catalog service
    So that I can keep track of all my wishlists

Background:
    Given the following wishlists
        | name         | user_id    |  status    |
        | electronics  | 101        |  Enabled   |
        | black_friday | 102        |  Enabled   |
        | phones       | 103        |  Disabled  |


     Given the following items
         | wishlist_name | product_id | product_name |
         | electronics   | 1          | iMac         |
         | electronics   | 2          | laptop       |
         | black_friday  | 3          | bose         |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all wishlists and items
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "electronics" in the results
    And I should see "phones" in the results
    And I should see "black_friday" in the results
    And I should see "iMac" in the item_results
    And I should see "laptop" in the item_results
    And I should see "bose" in the item_results

Scenario: Add an item and List all items of a wishlist
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "electronics" in the results
    And I should see "phones" in the results
    And I should see "black_friday" in the results
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I set the "name" to "electronics"
    And I press the "Search" button
    Then I should see "electronics" in the "Name" field
    And I should see "101" in the "User_ID" field
    And I should see "Enabled" in the "status" dropdown
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I press the "Item-Page" button
    And I paste the item "Wishlist_ID" field
    And I set the item "Product_ID" to "3"
    And I set the item "Product_Name" to "iPhone"
    And I press the item "Create" button
    Then I should see the message "Success"
    When I copy the item "Wishlist_ID" field
    And I press the item "Clear" button
    Then the item "Wishlist_Id" field should be empty
    And the item "Product_ID" field should be empty
    And the item "Product_Name" field should be empty
    When I paste the item "Wishlist_ID" field
    And I press the item "Search" button
    Then I should see "iMac" in the results
    And I should see "laptop" in the results
    And I should see "iPhone" in the results



Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "name" to "wishlist1"
    And I set the "User_ID" to "10"
    And I select "Enabled" in the "status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "wishlist1" in the "Name" field
    And I should see "10" in the "User_ID" field
    And I should see "Enabled" in the "status" dropdown

Scenario: Query a Wishlist
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "electronics" in the results
    And I should see "phones" in the results
    And I should see "black_friday" in the results
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I set the "name" to "electronics"
    And I press the "Search" button
    Then I should see "electronics" in the "Name" field
    And I should see "101" in the "User_ID" field
    And I should see "Enabled" in the "status" dropdown
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I set the "user_id" to "102"
    And I press the "Search" button
    Then I should see "black_friday" in the "Name" field
    And I should see "102" in the "User_ID" field
    And I should see "Enabled" in the "status" dropdown

Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "electronics" in the results
    Then I should not see "new_year" in the results
    And I should see "phones" in the results
    And I should see "black_friday" in the results
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I set the "name" to "electronics"
    And I press the "Search" button
    Then I should see "electronics" in the "Name" field
    And I should see "101" in the "User_ID" field
    And I should see "Enabled" in the "status" dropdown
    And I should not see "phones" in the results
    When I set the "name" to "new_year"
    When I set the "user_id" to "104"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "new_year" in the "Name" field
    And I should see "104" in the "User_ID" field
    And I should see "Enabled" in the "status" dropdown
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I press the "Search" button
    Then I should not see "electronics" in the results
    Then I should see "new_year" in the results
    And I should see "phones" in the results
    And I should see "black_friday" in the results

Scenario: Delete a Wishlist
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "electronics" in the results
    And I should see "phones" in the results
    And I should see "black_friday" in the results
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I set the "name" to "electronics"
    And I press the "Search" button
    Then I should see "electronics" in the "Name" field
    And I should see "101" in the "User_ID" field
    And I should see "Enabled" in the "status" dropdown
    When I press the "Delete" button
    Then I should see the message "Wishlist has been deleted"
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I press the "Search" button
    Then I should not see "electronics" in the results
    And I should see "phones" in the results
    And I should see "black_friday" in the results

Scenario: Update status of a Wishlist
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "phones" in the results
    And I should see "black_friday" in the results
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I set the "name" to "electronics"
    And I press the "Search" button
    Then I should see "electronics" in the "Name" field
    And I should see "101" in the "User_ID" field
    And I should see "Enabled" in the "status" dropdown
    When I select "Disabled" in the "status" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I set the "name" to "electronics"
    And I press the "Search" button
    Then I should see "electronics" in the "Name" field
    And I should see "101" in the "User_ID" field
    And I should see "Disabled" in the "status" dropdown

Scenario: Get Item by Item Id
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "electronics" in the results
    Then I should not see "new_year" in the results
    And I should see "phones" in the results
    And I should see "black_friday" in the results
    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "User_ID" field should be empty
    When I set the "name" to "black_friday"
    And I press the "Search" button
    Then I should see "black_friday" in the "Name" field
    And I should see "102" in the "User_ID" field
    And I should see "Enabled" in the "status" dropdown
    And I should not see "phones" in the results
    When I copy the "Id" field
    And I press the "Item-Page" button
    When I paste the item "Wishlist_ID" field
    And I press the item "Search" button
    Then I should not see "iMac" in the results
    And I should not see "laptop" in the results
    And I should see "bose" in the results
    When I set the item "Product_ID" to " "
    And I set the item "Product_Name" to " "
    And I press the item "Search" button
    Then I should not see "iMac" in the results
    And I should not see "laptop" in the results
    And I should see "bose" in the results
