# OptiHPLCHandler

Simplified proxy API for interacting with the Waters Empower Web API.

## Getting started

You can get the repo by cloning it from github at the URL
`https://github.com/novonordisk-research/OptiHPLCHandler.git`.

If you can't clone the repo on a Windows machine, you might need to set the SSL backend.
Run the following command in a terminal:
`git config --global http.sslbackend schannel`

It is recommended to make and activate a virtual environment by running the following
commands

```
pip install venv
python -v venv .env
.\.env\Scripts\activate
```

You need to run the last command every time you restart the computer

When the virtual environment is activated, install the package locally as an editable
installation

```
pip install -e .[dev]
```

If this doesn't work, you might need to upgrade pip and/or setuptools:

```
.\.env\scripts\python.exe -m pip install --upgrade pip
.\.env\scripts\python.exe -m pip install --upgrade setuptools
```

You should then be able to install the package locally as an editable installation.
