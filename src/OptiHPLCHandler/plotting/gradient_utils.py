def order_gradient_table(gradient_table: list[dict]) -> list[dict]:
    """
    Orders the gradient table by Time.
    """
    other_rows = [row for row in gradient_table if row["Time"] != "Initial"]
    other_rows.sort(key=lambda row: float(row["Time"]))
    initial_row = [row for row in gradient_table if row["Time"] == "Initial"]
    result = []
    result.extend(initial_row)
    result.extend(other_rows)
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
