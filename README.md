# OptiHPLCHandler

Simplified proxy API for interacting with the Waters Empower Web API.

## Using the package

The package can be installed into a Python environment with the command

```
pip install Opti-HPLC-Handler
```

You can then import packge and start an `EmpowerHandler`. You need to select the Empower
project to log in to. Note that the user logging in needs to have access to both that
project, and the project `Mobile`.

```
from OptiHPLCHandler import EmpowerHandler
handler=EmpowerHandler(project="project", address="https://API_url.com:3076")
```

your username will be auto-detected. Add the input `username` to use another account.

You will be prompted you for your password. The password will only be used to get a
token from the Empower Web API. When the token runs out, you will have to input your
passwrod again.

You can now get a list of the methodset methods in the project:

```
handler.GetMethodList()
```

To create a new sampleset method, first create it as a list of dicitonaries. Each
dictionary must have the keys `Method`, `SamplePos`, `SampleName`, and
`Injectionvolume`. If you want to populate oher fields, also add a key called
`OtherFields`, with a value that is a list of dicts, each dict having the keys `name`
and `value`:

```
sample_list = [
    {
        "Method": "test_method_1",
        "SamplePos": "test_sample_pos_1",
        "SampleName": "test_sample_name_1",
        "InjectionVolume": 1,
    },
    {
        "Method": "test_method_2",
        "SamplePos": "test_sample_pos_2",
        "SampleName": "test_sample_name_2",
        "InjectionVolume": 2,
        "OtherFields": [
            {"name": "test_field_1", "value": "test_value"},
            {"name": "test_field_2", "value": 2.3},
        ],
    },
]
```

At the moment, only Injection Sampleset lines are supported, but the injection volume
can be set to 0.

You can then use the handler to create the sampleset:

```
handler.PostExperiment(
    sample_set_method_name="test_sampleset_method_name",
    sample_list=sample_list,
    plate_list=[],
    audit_trail_message="test_audit_trail_message",
)
```

Note that `plate_list` should be filled out in order to run the sampleset.

You can run a sampleset method to create a sampleset:

```
handler.RunExperiment(
    sample_set_method="test_sampleset_method_name",
    hplc = "test_hplc",
)
```

## Getting started with developing the package

You can get the repo by cloning it from github at the URL
`https://github.com/novonordisk-research/OptiHPLCHandler.git`.

If you can't clone the repo on a Windows machine, you might need to set the SSL backend.
Run the following command in a terminal:
`git config --global http.sslbackend schannel`

It is recommended to make and activate a virtual environment by running the following
commands

```
pip install venv
python -m venv .env
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

## Releasing

To release a new version, get all of the changes you want into the branch `main`.
Then manually run the
[release GitHub action](https://github.com/novonordisk-research/OptiHPLCHandler/actions/workflows/release.yml)
by clicking `Run workflow`. Select what type of release it is by typing in `--patch`, `--minor`, or `--major` in `The type of release to perform`, and then click `Run workflow`.

Fetch the new branch `release`. Make sure there isn't a `dist` folder in
your project folder (or delete it), and run the commands

```
py -m build
py -m twine upload dist/*
```

you will be prompted for your pipy.org username and password.

In GitHub, merge the `release` branch into the `main` branch by
[creating a pull request](https://github.com/novonordisk-research/OptiHPLCHandler/compare/main...release)
and merging it.
