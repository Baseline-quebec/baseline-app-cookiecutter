# {{ cookiecutter.project_name }}

## Description

{{ cookiecutter.project_description }}

## Table of contents

1. [Setup](#setup)
2. [Usage](#usage)

## Setup

### Environment variables

To use this project, you need to set the environment variables. To do so, create a copy of the `.env.sample` file and name it `.env`. Then, fill in the values of the variables.

### Requirements

The set of requirements is dependent on how you want to run the application: locally or in a container.

#### Local setup

To use the application source code, you must have the following tools installed:

- [Python 3.12](https://www.python.org/downloads/) (the exact version is important)
- [Poetry](https://python-poetry.org/docs/#installation) (the exact version is not important, but there are some differences between major versions)

Check that the tools have been correctly installed by executing the following commands in your terminal:

```bash
python --version
```

```bash
poetry --version
```

To install the project dependencies, run the following command at the project's root:

```bash
poetry install
```

This will create a virtual environment and install the dependencies in it at the root of the project in a folder named `.venv`.

You can then activate the virtual environment created by Poetry (version less than 2.0) by running the following command:

```bash
poetry shell
```

If you are using Poetry version 2.0 or higher, you need to install the [plugin](https://python-poetry.org/docs/plugins/#using-plugins) `poetry-plugin-shell` before running the previous command. You can do so by running the following command:

```bash
poetry self add poetry-plugin-shell
```

#### Container setup

To use the application in a docker container, you must have Docker Desktop installed:

- [Docker](https://docs.docker.com/get-docker/)

## Usage

### Local usage

The project uses `poe-the-poet` as a CLI tool to manage the application. The commands are defined in the `pyproject.toml` file. To see available commands, you can run the following command at the project's root:

```bash
poe
```

To run the application locally, you need to execute the following command at the project's root:

```bash
poe api --dev
```

This will start the application in development mode. You can then access the API at the following URL: [`http://localhost:8000`](http://localhost:8000).

The API documentation is available at the following URL: [`http://localhost:8000/docs`](http://localhost:8000/docs). You can use it to test the different endpoints of the API.

### Container usage

To run the application in a container, you need to execute the following command at the project's root:

```bash
docker compose up app
```

This will start the application in a container. You can then access the API at the following URL: [`http://localhost:8000`](http://localhost:8000).

## Project structure

The project is structured as follows:

- `src/`: Contains the source code of the application.
- `tests/`: Contains the unit and integration tests of the application.
- `docs/`: Contains the ADRs and configuration guides.

At the root, you will find the `Dockerfile` and a `docker-compose.yml` file to facilitate the deployment of the application. There is also a `pyproject.toml` file that contains the Poetry project configuration, as well as READMEs for project documentation.
Pour contribuer au projet, lire le fichier [CONTRIBUTING.md](CONTRIBUTING.md).
