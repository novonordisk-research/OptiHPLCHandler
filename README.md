# OptiHPLCHandler

Simplified proxy API for interacting with the Waters Empower Web API. It aims to make
putting data into and getting data out of Empower easy, with the aim of automating
running samples. It will not feature changing data already in Empower.

## Using the package

The package can be installed into a Python environment with the command

```
pip install Opti-HPLC-Handler
```

You can then import package and start an `EmpowerHandler`. You need to select the Empower
project to log in to. Note that the user logging in needs to have access to both that
project, and the project `Mobile`.

```
from OptiHPLCHandler import EmpowerHandler
handler=EmpowerHandler(project="project", address="https://API_url.com:3076")
```

Your username will be auto-detected. Add the argument `username` to circumvent this
auto-detection.

EmpowerHandler will first try to find a password for Empower for the `username` in the
OS's system keyring, e.g. Windows Credential Locker. If it can't access a system
keyring, or the keyring does not contain the relevant key, you will be prompted you for
the password. The password will only be used to get a token from the Empower Web API.
When the token runs out, you will have to input your password again.

If you get the password from another source, e.g. a UI element, you can also provide it
directly when initialising the handler:

```
handler=EmpowerHandler(
   project="project",
   address="https://API_url.com:3076",
   password="password",
)
```

You can now get a list of the methodset methods in the project:

```
method_list = handler.GetMethodList()
```

You can also get the plate types that can be used in the project, the method
`handler.GetPlateTypeNames` is used. If you run it without arguments, it returns all
possible plate type names. You can also give it a `filter_string`. In that case, only
the plate types with names that contain the filter string are returned. You can then
define the plate setup of your HPLC:

```
plate_type_name_list = handler.GetPlateTypeNames(filter_string="48")
plates = {"1": plate_type_name_list[0], "2": plate_type_name_list[1]}
```

You can also have the plate list be empty, but you will then have to fill it out in
Empower before you can run the SampleSetMethod:

```
plates = {}
```

To create a new sampleset method, first create its sample list as a list of
dictionaries. Each dictionary must have the keys `SampleName`. The key `Method` is
intepreted as the Empower field `MethodSetOrReportMethod`, the key `SamplePos` as the
Empower field `Vial`, and the key `Injectionvolume` as the Empower field `InjVol`. Note
that if the dictionary contains both of one of these pairs, it is not predictable which
will be used. Additional keys are interpreted as Empower fields with the key value
as its name.

```
sample_list = [
    {
        "Method": method_list[0],
        "SamplePos": "1:A,1",
        "SampleName": "test_sample_name_1",
        "InjectionVolume": 1,
    },
    {
        "Method": method_list[1],
        "SamplePos": "2:A,1",
        "SampleName": "test_sample_name_2",
        "InjectionVolume": 2,
        "test_field_1": "test_value",
        "test_field_2" 2.3,
    },
]
```

At the moment, only Injection Sampleset lines are supported, but the injection volume
can be set to 0.

At the moment, `components` can only be an empty list.

You can then use the handler to create the sampleset:

```
handler.PostExperiment(
    sample_set_method_name="test_sampleset_method_name",
    sample_list=sample_list,
    plates=plates,
    audit_trail_message="test_audit_trail_message",
)
```

To run the a SampleSetmethod, you need to provide a node name and a chromatograpic
system name. If you don't know them, you can find them with `handler.GetNodeName()` and
`handler.GetSystemName(node = "node_name")`.

You can now run a sampleset method to create a sampleset:

```
handler.RunExperiment(
    sample_set_method="test_sampleset_method_name",
    sample_set_name="test_sample_set",
    node="node_name",
    hplc="test_hplc",
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

You need to run the last command every time you restart the computer.

When the virtual environment is activated, install the package locally as an editable
installation:

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
by clicking `Run workflow`. Select what type of release it is (`patch`, `minor`, or
`major`) in `The type of release to perform`, and then click `Run workflow`.

Fetch the new tag. Run the commands

```
rm -r -fo dist
py -m build
py -m twine upload dist/*
```

you will be prompted for your pipy.org username and password.
