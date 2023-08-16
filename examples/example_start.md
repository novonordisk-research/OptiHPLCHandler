# Examples

Outlined here are some example .ipynb files from use of OptiHPLCHandler

## Example: Basic usage - example_basicusage.ipynb
Here outlines a basic usage example of OptiHPLCHandler's EmpowerHandler.
* Installation & updating
* Connection token
* Get attributes
    * GetMethodList
    * GetSetup
    * GetNodeNames
    * GetSystemNames
    * GetPlateTypeNames
* Defining a sample set method
* Posting a sample set method
* Running a sample set method

## Example: Varying Injection Volume (Linearity) - example_linearity.ipynb
Here outlines a basic linearity experiment where one sample (and therefore one vial location) is injected at varying injection volumes. 
* Varies injection volume within a range in a defined incerement
* Samples in sample set defined in for loop, varying the injection volumne

## Example: Varying Sample Location - example_multivial.ipynb
Here outlines a basic sample set method where the sample position is incremented depending on the defined plate.
* Plate sample position logic defined (for ANSI-48Vial2mLHolder) 
* Samples in sample set defined in for loop, varying the sample position