Feature: Returning an object given a fixed URL
Scenario: Return a sample JSON
    Given the mock url
    When I go to '/hello-world/'
    Then I should get a '200' response
    And I should get a 'hello world!' message