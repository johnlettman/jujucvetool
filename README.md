<div align="center">

![Screenshot][screenshot]

# Juju CVE Tool
A highly automated tool for examining [Critical Vulnerabilities and Exposures][wiki-cve] on Ubuntu systems managed by Juju.

<hr>
</div>

## Features
- Human-friendly colorized CLI interactions
- Transparent access to local or remote environments
- Sub-commands for examining the package versions installed on machines

## Getting Started
### Installing Dependencies
First, make sure you have Poetry installed. If not, please refer to the
[Poetry installation guide](https://python-poetry.org/docs/#installation).
Then, install all the required dependencies for `jujucvetool`:

```bash
poetry install
```

This command will create the virtual environment and install all the necessary packages as defined in
[`pyproject.toml`](pyproject.toml).

### Using jujucvetool
Once installed, you can interact with the `jujucvetool` directly:

```bash
poetry run python -m jujucvetool --help
```

### Interacting with the Development Environment
#### Entering the Virtual Environment
To work within the virtual environment created by Poetry:

```bash
poetry shell
```

This will activate the virtual environment.
You will need to do this each time you start a new session.

#### Running jujucvetool
To run `jujucvetool` within the virtual environment:

```bash
python -m jujucvetool --help
```

#### Performing checks locally
```bash
# Lint import order with isort
poetry run isort ./jujucvetool --check

# Fix import order with isort
poetry run isort ./jujucvetool

# Lint with flake8
poetry run flake8 ./jujucvetool

# Lint with mypy
poetry run mypy ./jujucvetool

# Lint code format with black
poetry run black ./jujucvetool --check

# Fix code format with black
poetry run black ./jujucvetool

# Execute unit tests
poetry run pytest -s
```


[screenshot]: .github/assets/screenshot.png
[wiki-cve]: https://en.wikipedia.org/wiki/Common_Vulnerabilities_and_Exposures
