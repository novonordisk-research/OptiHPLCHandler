def make_method_name_string_compatible_with_empower(method_name: str) -> str:
    # Move to Empower_module_method
    """
    Replaces special characters in empower method names.

    Args:
        method_name (str): The original method name.

    Returns:
        str: The method name with special characters replaced.
    """

    new_method_name = method_name.replace(".", "_")
    new_method_name = new_method_name.replace("-", "m")  # assuming minus
    return new_method_name


def append_truncate_method_name(method_name: str, suffix: str) -> str:
    # Move to Empower_module_method
    """
    Truncates the given method name and appends the provided suffix.
    Also replaces characters that are not allowed in Empower method names.

    Args:
        method_name (str): The original method name.
        suffix (str): The suffix to be appended.

    Returns:
        str: The truncated method name with the suffix.
    """

    # Truncate
    if len(method_name) > 30 - len(suffix):
        new_method_name = method_name[: 30 - len(suffix)] + suffix
    else:
        new_method_name = method_name + suffix

    # Replace special characters
    new_method_name = make_method_name_string_compatible_with_empower(new_method_name)

    return new_method_name
