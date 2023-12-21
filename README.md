# OptiHPLCHandler

<a href="https://pypi.python.org/pypi/Opti-HPLC-Handler"><img src="https://img.shields.io/pypi/v/Opti-HPLC-Handler.svg" alt="PyPI Version"></a>
<a href="https://zenodo.org/doi/10.5281/zenodo.8386699"><img src="https://zenodo.org/badge/673355902.svg" alt="Zenodo DOI"></a>
<a href="https://github.com/novonordisk-research/OptiHPLCHandler/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/Opti-HPLC-Handler.svg" alt="License"></a>
<a href="https://pepy.tech/project/opti-hplc-handler"><img src="https://img.shields.io/pypi/dm/Opti-HPLC-Handler.svg" alt="PyPI Downloads"></a>
<a href="https://github.com/novonordisk-research/OptiHPLCHandler"><img src="https://img.shields.io/github/last-commit/novonordisk-research/OptiHPLCHandler.svg" alt="Source code on GitHub"></a>

Simplified proxy API for interacting with the Waters Empower Web API. It aims to make
putting data into and getting data out of Empower easy, with the aim of automating
running samples. It will not feature changing data already in Empower.

## Using the package

The package can be installed into a Python environment with the command

```
pip install Opti-HPLC-Handler
```

You can then import package and start an `EmpowerHandler`. You need to select the
Empower project to log in to. Note that the user logging in needs to have access to both
that project, and the project `Mobile`.

```python
from OptiHPLCHandler import EmpowerHandler
handler=EmpowerHandler(
    project="project",
    address="https://API_url.com:3076",
    allow_login_without_context_manager=True,
)
```

Your username will be auto-detected. Add the argument `username` to circumvent this
auto-detection.

`EmpowerHandler` will first try to find a password for Empower for the `username` in the
OS's system keyring, e.g. Windows Credential Locker. If it can't access a system
keyring, or the keyring does not contain the relevant key, you will be prompted you for
the password. The password will only be used to get a token from the Empower Web API.
When the token runs out, you will have to input your password again.

To log in, use the `EmpowerHandler` with a context manager:

```python
handler=EmpowerHandler(
    project="project",
    address="https://API_url.com:3076",
)
with handler:
    ...
```

If you get the password from another source, e.g. a UI element, you can also manually
log in with the password. In order to use this with a context manger, you
need set `EmpowerHandler` to not log in when entering the context:

```python
handler=EmpowerHandler(
    project="project",
    address="https://API_url.com:3076",
    auto_login=False,
)
with handler:
    handler.login(username="username", password="password")
    ...
```

When logged in, the `EmpowerHandler` can be used to access an authorisation key that can
be used for the Web API directly:

```python
handler.connection.authorization_header["Authorization"]
```

The authorisation key must be given in the HTTP header with the name `Authorization`.
If you are using `requests`, you can simply provide
`handler.connection.authorization_header` as `headers` in the request.

## Instrument methods

You can now get a list of the instruement methods in the project:

```python
method_list = handler.GetMethodList(method_type="Instrument")
```

You can get one such method and inspect its contents:

```python
import pprint

pp = pprint.PrettyPrinter(indent=2)
full_method = handler.GetInstrumentMethod(method_name)
print(f"Valve positions: {full_method.instrument_method_list[-1].valve_position}")
print(f"Column temperature: {full_method.column_temperature}")
print("\n\nStart of gradient table:\n")
pp.pprint(full_method.gradient_table[0:2])
```

The created `EmpowerInstrumentMethod` object allows for changes, and remembers both the
original method as it was in Empower, and the current mehtod with all changes made. It
has the following properties:

- `original_method`
- `current_method`: The current method definition, with any changes applied.
- `column_oven_list`: A list of column ovens in the method set method. By default, only
  column managers are included, but you can include sample manager column ovens by
  creating it with
  `handler.GetInstrumentMethod(method_name, use_sample_manager_oven=True)`.
- `module_method_list`
- `solvent_handler_method`: Will be `None` if no solvent handler is included in the
  method.
- `column_temperature`: If multiple column ovens are used, the temperature is only
  returned if all column ovens have the same temperature. Otherwise, a `ValueError` is
  raised. If no column ovens are found, a `ValueError` is raised. When setting the
  column temperature, all column ovens will be set to the same temperature, regardless
  of the original temperatures. If no column ovens are found, a `ValueError` is raised.
- `gradient_table`
- `valve_position`

Accessing or setting `gradient_table` or `valve_position` will result in a `ValueError`
if no solvent handler is included in the method.

You can modify the method, give it a new name, and post it to Empower:

```python
gradient_table = full_method.gradient_table
for step in gradient_table:
    step["Flow"] = 0.5
full_method.gradient_table = gradient_table
full_method.valve_position = ["A2", "B1"]
full_method.column_temperature = 40
full_method.method_name ="New method name"
with handler:
    handler.PostInstrumentMethod(full_method) # Post the updated method to Empower
```

## Sampleset method

You can also get a list of the sample set methods in the project:

```python
sampleset_list = handler.GetMethodList(method_type="SampleSet")
```

You can also get the plate types that can be used in the project, the method
`handler.GetPlateTypeNames` is used. If you run it without arguments, it returns all
possible plate type names. You can also give it a `filter_string`. In that case, only
the plate types with names that contain the filter string are returned. You can then
define the plate setup of your HPLC:

```python
plate_type_name_list = handler.GetPlateTypeNames(filter_string="48")
plates = {"1": plate_type_name_list[0], "2": plate_type_name_list[1]}
```

You can also have the plate list be empty, but you will then have to fill it out in
Empower before you can run the SampleSetMethod:

```python
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
    system="test_hplc",
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

The workflow should create a branch, a tag, a pull request, a Github release and a pypi
release.

After the workflow is done, you need to approve the pull request.
