# Examples Outline

Here is an outline of all the current examples.

## Example: [Basic Usage](example_basicusage.ipynb)

Here outlines the basic usage of EmpowerHandler in OptiHPLCHandler. This includes:

- Installation & updating
- Importing and login
- Connection token (For easy EmpowerAPI access)
- Get attributes of EmpowerHandler
  - GetMethodList()
  - GetSetup()
  - GetNodeNames()
  - GetSystemNames()
  - GetPlateTypeNames()
- Sample set method creation
- Sample set method posting to Empower
- Sample set method running on chosen system

## Example: [Varying Injection Volume (Linearity)](example_linearity.ipynb)

Here outlines a basic linearity experiment where one sample (and therefore one vial location) is injected at varying injection volumes.

- Varies injection volume within a range in a defined increment.
- Samples in sample set defined in for loop, varying the injection volume.

## Example: [Varying Sample Positions (examples_multivial.ipynb)](example_multivial.ipynb)

Here outlines a basic sample set method where the sample position is incremented depending on the defined plate.

- Plate sample position logic defined (for ANSI-48Vial2mLHolder).
- Samples in sample set defined in for loop, varying the sample position.

## Example: [Get, inspect, change, and put back a methodset method](example_methodset_method.ipynb)

Here outlines how to interact with methodset methods and instrument methods.

- Finding and getting a methodset method.
- Inspecting what types of instrument methods are in the methodset method.
- Inspecting the instrument parameters in the method, including column temperature and gradient table.
- Changing instrument parameters and posting the new method.
