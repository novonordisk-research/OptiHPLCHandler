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

## Example: [Moving and Saving Logins](example_moving_and_saving_logins.ipynb)

Here outlines how to reuse a login from one `EmpowerHandler` instance in another, e.g. between a frontend and a backend.

- Extracting the token and session ID from a logged-in handler
- Passing them into a new handler
- Manually setting synonyms and enumerated fields that are otherwise set during login

## Example: [Components](example_components.ipynb)

Here outlines how to define standard concentrations using the Empower components field.

- Components defined as a dict of compound names and concentrations per standard
- Using a custom key for components when a custom field is named Components

## Example: [Varying Injection Volume (Linearity)](example_linearity.ipynb)

Here outlines a basic linearity experiment where one sample (and therefore one vial location) is injected at varying injection volumes.

- Varies injection volume within a range in a defined increment.
- Samples in sample set defined in for loop, varying the injection volume.

## Example: [Varying Sample Positions (examples_multivial.ipynb)](example_multivial.ipynb)

Here outlines a basic sample set method where the sample position is incremented depending on the defined plate.

- Plate sample position logic defined (for ANSI-48Vial2mLHolder).
- Samples in sample set defined in for loop, varying the sample position.

## Example: [Get, inspect, change, and put back a instrument method](example_instrument_method.ipynb)

Here outlines how to interact with instrument methods and instrument methods.

- Finding and getting a instrument method.
- Inspecting what types of instrument methods are in the instrument method.
- Inspecting the instrument parameters in the method, including column temperature and gradient table.
- Changing instrument parameters and posting the new method.

## Example: [Detectors](example_detectors.ipynb)

Here outlines how to inspect and change detector channels in PDA, TUV and FLR methods.

- Setting channels with the channels attribute (PDAChannel, TUVChannel, FLRChannel)
- Setting channels with the wavelengths attribute
- PDA spectral channel on the detector method level
- TUV switching between single and dual mode

## Example: [Method Transfer](example_method_transfer.ipynb)

Here outlines how to convert methods between pump and detector types.

- Converting gradient tables between BSM and QSM methods, for gradient and isocratic flow
- Converting between detector types using the channels or wavelengths attribute

## Example: [Gradient Plot](example_gradient_plot.ipynb)

Here outlines how to plot gradient tables.

- Generating plot coordinates from a gradient table for all curve types
- Overlaying gradients in a single plotly figure

## Example: [Method generation from an input instrument method](example_method_generators.ipynb)

Here outlines a series of method generators that takes an input instrument method and generates a variety of methods from them.

- Generates a ramp-up method of the input method, taking the first row of the gradient table as the basis and ramping the flow rate slowly over a period of time to elongate column life-time and prevent huge pressure spikes.
- Generates a condensed version of the input methods gradient to condition the column prior to use.
- Generates a version of the method where the temperature is changed by a certain value eg. +/- 5 °C
- Generates a method that has the same gradient slope as the initial method, but with a different value of the strong eluent. eg. +/- 1 %B
- Generates a method with an isocratic step in a defined place in the gradient table. eg. a 10 minute isocratic start

## Example: [Using method generation, makes a basic robustness sample set for an defined input method](example_robustness.ipynb)

Here outlines the use of the above method generators, making a sample set method to test the robustness of the method.

## Example: [Column Eluent Screening Experiment](example_column_eluent_screening.ipynb)

Here outlines an example of how one could conduct a column eluent screening experiment. 

- Based on template method, generates a matrix of instrument methods
- Populates a sample set method

## Example: [Stability Study Experiment](example_stability_study.ipynb)

Here outlines an example of how one could conduct a stability study. With a sample incubated at different temperatures and taken out of incubation at different timepoints.

- Based on template method, alters method to make sure gradient table and valves are set to correct lines.
- Populates a sample set method

## Example: [Getting Sample Sets](example_sample_sets.ipynb)

Here outlines how to query sample set data in a project.

- GetFieldNames() to find available sample set fields
- GetSampleSets() with filtering and sorting, and GetSampleSetsRaw() for the raw response

## Example: [Getting Results and Peaks](example_results_and_peaks.ipynb)

Here outlines how to query processed results and their peak data.

- GetFieldNames() to find available result and peak fields
- GetResult() for all fields of one result ID
- GetResults() by searching on a result field, with paging, and GetResultsRaw() for the raw response
- GetPeaks() for a list of result IDs