"""Pre-generation hook: validate cookiecutter inputs."""

import re
import sys

project_name = "{{ cookiecutter.project_name }}"
python_version = "{{ cookiecutter.python_version }}"
with_sentry = int("{{ cookiecutter.with_sentry }}")
with_fastapi_api = int("{{ cookiecutter.with_fastapi_api }}")

# Validate project_name: letters, digits, spaces, hyphens.
if not re.match(r"^[A-Za-z0-9 -]+$", project_name):
    print(
        f"ERROR: Invalid project_name '{project_name}'. "
        "Only letters, digits, spaces, and hyphens are allowed."
    )
    sys.exit(1)

# Validate python_version >= 3.10.
try:
    major, minor = (int(x) for x in python_version.split(".")[:2])
    if (major, minor) < (3, 10):
        print(f"ERROR: python_version must be >= 3.10, got '{python_version}'.")
        sys.exit(1)
except ValueError:
    print(f"ERROR: Invalid python_version '{python_version}'.")
    sys.exit(1)

# Warn if Sentry is enabled without FastAPI.
if with_sentry and not with_fastapi_api:
    print(
        "WARNING: with_sentry=1 has no effect without with_fastapi_api=1. "
        "Sentry integration requires FastAPI."
    )
