"""Post-generation hook: remove files based on cookiecutter options."""

import os
import shutil
from pathlib import Path

# Read Cookiecutter configuration.
project_name = "{{ cookiecutter.__project_name_snake_case }}"
development_environment = "{{ cookiecutter.development_environment }}"
with_conventional_commits = int("{{ cookiecutter.with_conventional_commits }}")
mcp_profile = "{{ cookiecutter.mcp_profile }}"
with_fastapi_api = int("{{ cookiecutter.with_fastapi_api }}")
with_typer_cli = int("{{ cookiecutter.with_typer_cli }}")
with_pytest_bdd = int("{{ cookiecutter.with_pytest_bdd }}")
license_choice = "{{ cookiecutter.license }}"

# Remove PR title check workflow if conventional commits is disabled.
if not with_conventional_commits:
    os.remove(".github/workflows/pr.yml")

# Remove py.typed and Dependabot if not in strict mode.
if development_environment != "strict":
    os.remove(f"src/{project_name}/py.typed")
    os.remove(".github/dependabot.yml")

# Remove FastAPI if not selected.
if not with_fastapi_api:
    os.remove(f"src/{project_name}/api.py")
    os.remove(f"src/{project_name}/models.py")
    os.remove(f"src/{project_name}/services.py")
    os.remove("tests/test_api.py")
    if with_pytest_bdd:
        os.remove("tests/features/api.feature")

# Remove Typer if not selected.
if not with_typer_cli:
    os.remove(f"src/{project_name}/cli.py")
    os.remove("tests/test_cli.py")
    if with_pytest_bdd:
        os.remove("tests/features/cli.feature")

# Remove .vscode/ directory if not using FastAPI (no launch.json needed).
if not with_fastapi_api and not with_typer_cli:
    shutil.rmtree(".vscode", ignore_errors=True)

# Remove BDD test infrastructure when pytest-bdd is not selected.
if not with_pytest_bdd:
    shutil.rmtree("tests/features", ignore_errors=True)

# Remove LICENSE file for proprietary projects.
if license_choice == "Proprietary":
    os.remove("LICENSE")

# ── MCP Profile: interactive server selection ───────────────────
BASELINE_DIR = Path.home() / ".baseline"
CONFIG_DIR = BASELINE_DIR / "mcp-config"
REGISTRY_PATH = CONFIG_DIR / "registry.yaml"
PROFILE_PATH = CONFIG_DIR / "profiles" / f"{mcp_profile}.yaml"

if REGISTRY_PATH.exists() and PROFILE_PATH.exists():
    try:
        import yaml

        with open(REGISTRY_PATH) as f:
            registry = yaml.safe_load(f)
        with open(PROFILE_PATH) as f:
            profile = yaml.safe_load(f)

        servers = profile["servers"]
        print(f"\n  Serveurs MCP du profil '{mcp_profile}':")
        for i, name in enumerate(servers, 1):
            server = registry["servers"].get(name, {})
            server_type = server.get("type", "?")
            print(f"    {i}. {name} ({server_type})")

        print(f"\n  Modifier la selection? (Enter pour accepter, ou +serveur/-serveur)")
        user_input = input("  > ").strip()

        if user_input:
            selected = set(servers)
            for token in user_input.split():
                if token.startswith("-"):
                    selected.discard(token[1:])
                elif token.startswith("+"):
                    server_name = token[1:]
                    if server_name in registry["servers"]:
                        selected.add(server_name)
                    else:
                        print(f"    ⚠ '{server_name}' n'existe pas dans le registry")

            # Write extended format with selected servers
            with open(".mcp-profile", "w") as f:
                f.write(f"profile: {mcp_profile}\nservers:\n")
                for s in selected:
                    f.write(f"  - {s}\n")
            print(f"  ✓ .mcp-profile ecrit ({len(selected)} serveurs)")
        else:
            print(f"  ✓ .mcp-profile ecrit (profil complet, {len(servers)} serveurs)")

    except ImportError:
        print("  ⚠ PyYAML non disponible — .mcp-profile ecrit avec le profil complet")
    except Exception as e:
        print(f"  ⚠ Erreur MCP: {e} — .mcp-profile ecrit avec le profil complet")
else:
    print(f"  ℹ mcp-config non installe — .mcp-profile ecrit avec le profil '{mcp_profile}'")
