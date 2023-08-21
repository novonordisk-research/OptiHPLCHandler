# Examples Outline
Here is an outline of all the current examples.

## Example: Basic Usage
Here outlines the basic usage of EmpowerHandler in OptiHPLCHandler. This includes:
* Installation & updating
* Importing and login
* Connection token (For easy EmpowerAPI access)
* Get attributes of EmpowerHandler
    * GetMethodList()
    * GetSetup()
    * GetNodeNames()
    * GetSystemNames()
    * GetPlateTypeNames()
* Sample set method creation
* Sample set method posting to Empower
* Sample set method running on chosen system

## Example: Varying Injection Volume (Linearity)
Here outlines a basic linearity experiment where one sample (and therefore one vial location) is injected at varying injection volumes. 
* Varies injection volume within a range in a defined incerement
* Samples in sample set defined in for loop, varying the injection volumne

## Example: Varying Sample Positions
Here outlines a basic sample set method where the sample position is incremented depending on the defined plate.
* Plate sample position logic defined (for ANSI-48Vial2mLHolder) 
* Samples in sample set defined in for loop, varying the sample position