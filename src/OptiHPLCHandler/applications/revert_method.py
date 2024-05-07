from OptiHPLCHandler import EmpowerInstrumentMethod


def revert_method(method: EmpowerInstrumentMethod, original_method_name: str):
    """
    Revert the instrument method to the method prior to changes.
    """

    for change in method.module_method_list:
        try:
            while True:
                change.undo()
        except IndexError as e:
            if str(e) == "pop from empty list":
                continue
            else:
                raise e

    method.method_name = original_method_name

    return method
