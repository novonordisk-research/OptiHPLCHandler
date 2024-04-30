from typing import List


def validate_gradient_table(gradient_table: List[dict]) -> bool:  # noqa:C901
    # Move to Empower_module_method
    """
    Validates the gradient table to ensure the sum of compositions in each row is 100.

    Args:
        gradient_table (List[dict]): The gradient table to validate.

    Returns:
        bool: True if the gradient table is valid, False otherwise.
    """
    previous_time = None
    for row in gradient_table:
        list_keys = row.keys()
        if any("Composition" in key for key in list_keys):
            # Test sum of compositions is 100
            sum_compositions = sum(
                float(value) for key, value in row.items() if "Composition" in key
            )
            if sum_compositions != 100:
                raise ValueError(
                    "The sum of the compositions in the gradient table row is not"
                    + f"equal to 100. The sum is {sum_compositions}. The row is {row}"
                )
        # if any composition is greater than 100 or less than 0
        for key in list_keys:
            if "Composition" in key:
                if float(row[key]) > 100 or float(row[key]) < 0:
                    raise ValueError(
                        "The composition in the gradient table row is greater than"
                        + f"100 or less than 0. The composition is {row[key]}."
                        + f"The row is {row}"
                    )

        # Test time is greater than previous time
        if "Time" in row:
            # if any other rows are inital other than first
            if row["Time"] == "Initial" and row != gradient_table[0]:
                raise ValueError(
                    "The time in the gradient table row is 'Initial' on a row other"
                    + f"than the first. The row is {row}"
                )
            if row["Time"] == "Initial":
                current_time = 0
            else:
                current_time = float(row["Time"])
            if previous_time is not None:
                if current_time < previous_time:
                    raise ValueError(
                        "The time in the gradient table row is less than the previous"
                        + f"row. The row is {row['Time']} and the previous row"
                        + f"is {previous_time}."
                    )
            previous_time = current_time

    return True
