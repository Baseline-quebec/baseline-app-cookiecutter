# {{ cookiecutter.project_name }}

## Description

{{ cookiecutter.project_description }}

## Exécution de l'application

To install this package, run:

```sh
pip install {{ cookiecutter.__project_name_kebab_case }}
```

## Using

{%- if cookiecutter.with_typer_cli|int %}

Pour voir les commandes disponibles: exécutez::

```sh
{{ cookiecutter.__project_name_kebab_case }} --help
```

{%- elif cookiecutter.project_type == "app" %}

Pour lancer l'application, exécutez:

```sh
docker compose up app
```

{%- if cookiecutter.with_fastapi_api|int %}

L'application sera accessible à l'adresse [localhost:8000](http://localhost:8000)..
{%- endif %}

Within the Dev Container this is equivalent to:

```sh
poe {% if cookiecutter.with_fastapi_api|int %}api{% else %}app{% endif %}
```

{%- else %}

Exemple d'utilisation:

```python
import {{ cookiecutter.__project_name_snake_case }}

...
```

{%- endif %}

## Utilisation du code source

Pour utiliser le code source de l'application, vous devez avoir les outils suivants installés sur votre machine:

- [Python 3.12](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)

Vérifiez que vous avez bien installé les outils en exécutant les commandes suivantes dans votre terminal:

```bash
python --version
```

puis

```bash
poetry --version
```

Pour installer les dépendances du projet, exécutez la commande suivante à la racine du projet:

```bash
poetry install
```

Vous pouvez ensuite activer l'environnement virtuel créé par Poetry en exécutant la commande suivante:

```bash
poetry shell
```

Pour lancer l'application en mode développement, exécutez la commande suivante:

```bash
poe api --dev
```

L'application sera accessible à l'adresse [localhost:8000](http://localhost:8000). Pour lancer l'application en mode production, voir la section [Déploiement](#déploiement).

Pour plus de détails sur les points d'entrée `poe` du projet, consultez le fichier [pyproject.toml](pyproject.toml).

## Structure du projet

Le projet est structuré de la manière suivante:

- `src/`: Contient le code source de l'application.
- `tests/`: Contient les tests unitaires et d'intégration de l'application.
- `docs/`: Contient les ADRs et les guides de configuration.

À la racine, on retrouve le `Dockerfile` et un `docker-compose.yml` pour faciliter le déploiement de l'application. On trouve aussi un fichier `pyproject.toml` qui contient la configuration du projet Poetry ainsi que les READMEs pour la documentation du projet.

## Développement

Pour contribuer au projet, lire le fichier [README.dev.md](README.dev.md).
