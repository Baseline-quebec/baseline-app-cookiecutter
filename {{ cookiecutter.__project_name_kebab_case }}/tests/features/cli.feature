Feature: CLI
  The CLI should execute commands correctly.

  Scenario: Info command displays metadata
    Given a CLI runner
    When I run the info command
    Then the exit code should be 0
    And the output should contain "{{ cookiecutter.project_name }}"

  Scenario: Config command displays settings
    Given a CLI runner
    When I run the config command
    Then the exit code should be 0
    And the output should contain "app_name"
{%- if cookiecutter.with_fastapi_api|int %}

  Scenario: Health command executes
    Given a CLI runner
    When I run the health command
    Then the exit code should be 0
{%- endif %}

  Scenario: Verbose flag is accepted
    Given a CLI runner
    When I run the info command with verbose
    Then the exit code should be 0
