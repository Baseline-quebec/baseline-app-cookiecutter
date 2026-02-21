Feature: REST API
  The API should handle requests correctly.

  Scenario: Compute endpoint returns success
    Given the API test client
    When I request computation with n=7
    Then the response should be successful
