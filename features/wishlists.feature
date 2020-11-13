Feature: The wishlist service back-end
    As a Wishlist Service Developer
    I need a RESTful catalog service
    So that I can keep track of all my wishlists

Background:
    Given the following wishlists
        | name        | user_id    | items      | status    |
        | electronics | 101        |     | True      |
        | phones      | 102        |     | True      |


    # Given the following items
    #     | wishlist_id | product_id | product_name |
    #     | 2           | 1          | iPhone       |
    #     | 1           | 2          | laptop       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all wishlists
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "electronics" in the results
    And I should see "phones" in the results

# Scenario: List all items
#     When I visit the "Home Page"
#     And I press the "Item Page" button
#     And I press the "Search" button
#     Then I should see "iPhone" in the results
#     And I should not see "laptop" in the results

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