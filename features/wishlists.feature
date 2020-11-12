Feature: The wishlist service back-end
    As a Wishlist Service Developer
    I need a RESTful catalog service
    So that I can keep track of all my wishlists

Background:
    Given the following wishlists
        | name        | user_id    | items      | status    |
        | electronics | 101        | [laptop]   | True      |
        | phones      | 102        | [iPhone]   | True      |


    Given the following items
        | wishlist_id | product_id | product_name |
        | 2           | 1          | iPhone       |
        | 1           | 2          | laptop       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all wishlists
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "electronics" in the results
    And I should see "phones" in the results

Scenario: List all items
    When I visit the "Home Page"
    And I press the "Item Page" button
    And I press the "Search" button
    Then I should see "iPhone" in the results
    And I should not see "laptop" in the results