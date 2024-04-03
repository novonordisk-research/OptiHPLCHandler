from OptiHPLCHandler import EmpowerHandler

# Create an instance of the EmpowerHandler class
handler = EmpowerHandler(project="WebAPI_test", address="XXXX")

# Get the list of methods, select one, and get the method details
with handler:
    method_list = handler.GetMethodList()  # Get the list of instrument methods
    method_name = method_list[0]  # Select the first method
    print(method_name)
    full_method = handler.GetInstrumentMethod(method_name)
