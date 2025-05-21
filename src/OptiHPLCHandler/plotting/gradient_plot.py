import numpy as np
import plotly.graph_objects as go


def plot_gradient_table(x, y, fill=True, fig=None) -> go.Figure:
    """
    Plots a gradient table.
    """
    if fig is None:
        fig = go.Figure()

    if fill:
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Flow", fill="tozeroy"))
    else:
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Flow"))

    return fig


def order_gradient_table(gradient_table: list[dict]) -> list[dict]:
    """
    Orders the gradient table by Time.
    """
    return sorted(
        gradient_table, key=lambda entry: (entry["Time"] != "Initial", entry["Time"])
    )


def standardise_gradient_table_types(gradient_table: list[dict]) -> list[dict]:
    """
    Standardises the types in the gradient table.
    Converts all values to floats, except for Time and Curve, which are converted to int
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


def generate_coordinates(
    gradient_table: list[dict], row_key
) -> tuple[list[float], list[float]]:
    """
    Generates x and y coordinates for the gradient table.
    """

    curve_dict = {  # the powers for each curve value
        2: 1 / 5,
        3: 1 / 4,
        4: 1 / 3,
        5: 1 / 2,
        6: 1,
        7: 2,
        8: 3,
        9: 4,
        10: 5,
    }

    gradient_table = standardise_gradient_table_types(gradient_table)
    x = []
    y = []

    previous_time = None
    previous_y = None
    for row in gradient_table:
        curve = row["Curve"]
        time = row["Time"]
        current_y = row[row_key]
        if curve == 0:
            # initial conditions
            pass

        elif curve == 11:
            # Stepwise at end
            # add a point prior to the step with the same composition as previous
            x.append(time - 0.01)
            y.append(previous_y)

        elif curve == 1:
            # stepwise at start
            # add a point prior to the step with the same composition as previous
            x.append(previous_time + 0.01)
            y.append(current_y)
        else:
            # numerically calculated gradient
            initial_condition = previous_y
            final_condition = current_y
            x_curve_to_add = np.linspace(
                previous_time + 0.01, time - 0.01, int((time - previous_time) / 0.1)
            )
            normalised_curve = (
                np.linspace(0, 1, len(x_curve_to_add)) ** curve_dict[curve]
            )  # Constructing the shape, with y values between 0 and 1
            y_curve_to_add = [
                y * (final_condition - initial_condition) + initial_condition
                for y in normalised_curve
            ]  # Scaling to the actual y values
            x.extend(x_curve_to_add)
            y.extend(y_curve_to_add)

        previous_time = time
        previous_y = current_y
        x.append(time)
        y.append(current_y)

    return x, y
