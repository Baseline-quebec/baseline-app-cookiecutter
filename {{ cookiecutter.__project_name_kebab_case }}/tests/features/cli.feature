Feature: CLI
  The CLI should execute commands correctly.

  Scenario: Fire command outputs name
    Given a CLI runner
    When I run the fire command with name "GLaDOS"
    Then the exit code should be 0
    And the output should contain "GLaDOS"
