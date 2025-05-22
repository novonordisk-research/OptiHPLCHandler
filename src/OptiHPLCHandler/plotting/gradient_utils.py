def order_gradient_table(gradient_table: list[dict]) -> list[dict]:
    """
    Orders the gradient table by Time.
    """
    initial_row = None
    other_rows = []
    for row in gradient_table:
        if row["Time"] == "Initial":
            initial_row = row  # Save to add to start later
        else:
            other_rows.append(row)
    for row in other_rows:
        row["Time"] = float(row["Time"])  # ensure float
    other_rows.sort(key=lambda entry: entry["Time"])  # order list by
    result = []
    if initial_row is not None:
        result.append(initial_row)  # Adds initial to start of results list
    result.extend(other_rows)  # Adds rest of the rows after
    return result


def standardise_gradient_table_types(gradient_table: list[dict]) -> list[dict]:
    """
    Standardises the types in the gradient table.
    Converts all values to floats, except for Curve, which is converted to int
    """

    gradient_table = order_gradient_table(gradient_table)
    for row in gradient_table:
        for key, value in row.items():
            if key == "Time":
                if value == "Initial":
                    row[key] = 0.0
                else:
                    row[key] = float(value)
            elif key == "Curve":
                if value == "Initial":
                    row[key] = 0
                else:
                    row[key] = int(value)
            else:
                row[key] = float(value)
    return gradient_table