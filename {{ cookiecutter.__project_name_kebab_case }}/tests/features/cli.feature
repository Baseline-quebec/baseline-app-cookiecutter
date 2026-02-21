Feature: CLI
  The CLI should execute commands correctly.

  Scenario: Info command displays metadata
    Given a CLI runner
    When I run the info command
    Then the exit code should be 0
    And the output should contain "{{ cookiecutter.project_name }}"

  Scenario: Greet command outputs name
    Given a CLI runner
    When I run the greet command with name "Alice"
    Then the exit code should be 0
    And the output should contain "Alice"

  Scenario: Verbose flag is accepted
    Given a CLI runner
    When I run the greet command with verbose and name "Bob"
    Then the exit code should be 0
    And the output should contain "Bob"
