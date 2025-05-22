import unittest

from OptiHPLCHandler.plotting.gradient_utils import (
    order_gradient_table,
    standardise_gradient_table_types,
)


class TestOrderGradientTable(unittest.TestCase):
    def setUp(self):
        self.unordered_gradient_table = [
            {"Time": "10", "CompositionA": 20, "Curve": 6},
            {"Time": "Initial", "CompositionA": 10, "Curve": "Initial"},
            {"Time": "5", "CompositionA": 15, "Curve": 1},
            {"Time": "20", "CompositionA": 25, "Curve": 7},
        ]
        self.unordered_gradient_table_types = [
            {"Time": 10, "CompositionA": 20, "Curve": 6},
            {"Time": "Initial", "CompositionA": 10, "Curve": "Initial"},
            {"Time": 5.0, "CompositionA": 15, "Curve": 1},
            {"Time": "20", "CompositionA": 25, "Curve": 7},
        ]

    def test_order_gradient_table_places_initial_first(self):
        ordered = order_gradient_table(self.unordered_gradient_table)
        self.assertEqual(ordered[0]["Time"], "Initial")
        self.assertEqual([row["Time"] for row in ordered[1:]], [5.0, 10.0, 20.0])

    def test_order_gradient_table_handles_no_initial(self):
        table = [
            row for row in self.unordered_gradient_table if row["Time"] != "Initial"
        ]
        ordered = order_gradient_table(table)
        self.assertEqual([row["Time"] for row in ordered], [5.0, 10.0, 20.0])

    def test_order_gradient_table_handles_only_initial(self):
        table = [
            {"Time": "Initial", "CompositionA": 10, "Curve": "Initial"},
        ]
        ordered = order_gradient_table(table)
        self.assertEqual(len(ordered), 1)
        self.assertEqual(ordered[0]["Time"], "Initial")

    def test_order_gradient_table_handles_types(self):
        table = self.unordered_gradient_table_types
        ordered = order_gradient_table(table)
        self.assertEqual(ordered[0]["Time"], "Initial")
        self.assertEqual([row["Time"] for row in ordered[1:]], [5.0, 10.0, 20.0])


class TestStandardiseGradientTableTypes(unittest.TestCase):
    def test_standardises_types_with_initial(self):
        table = [
            {"Time": "Initial", "CompositionA": "10", "Curve": "Initial"},
            {"Time": "5", "CompositionA": "15.5", "Curve": "1"},
            {"Time": "10", "CompositionA": 20, "Curve": 6},
        ]
        result = standardise_gradient_table_types(table)
        self.assertEqual(result[0]["Time"], 0.0)
        self.assertEqual(result[0]["CompositionA"], 10.0)
        self.assertEqual(result[0]["Curve"], 0)
        self.assertEqual(result[1]["Time"], 5.0)
        self.assertEqual(result[1]["CompositionA"], 15.5)
        self.assertEqual(result[1]["Curve"], 1)
        self.assertEqual(result[2]["Time"], 10.0)
        self.assertEqual(result[2]["CompositionA"], 20.0)
        self.assertEqual(result[2]["Curve"], 6)

    def test_standardises_types_without_initial(self):
        table = [
            {"Time": 0, "CompositionA": "15.5", "Curve": "1"},
            {"Time": "5", "CompositionA": "15.5", "Curve": "1"},
            {"Time": "10", "CompositionA": 20, "Curve": 6},
        ]
        result = standardise_gradient_table_types(table)
        self.assertEqual(result[0]["Time"], 0.0)
        self.assertEqual(result[0]["CompositionA"], 15.5)
        self.assertEqual(result[0]["Curve"], 1)
        self.assertEqual(result[1]["Time"], 5.0)
        self.assertEqual(result[1]["CompositionA"], 15.5)
        self.assertEqual(result[1]["Curve"], 1)
        self.assertEqual(result[2]["Time"], 10.0)
        self.assertEqual(result[2]["CompositionA"], 20.0)
        self.assertEqual(result[2]["Curve"], 6)

    def test_standardises_types_with_float_and_int(self):
        table = [
            {"Time": 0, "CompositionA": 10, "Curve": 0},
            {"Time": 5.0, "CompositionA": 15, "Curve": 1},
            {"Time": 10, "CompositionA": 20.0, "Curve": 6},
        ]
        result = standardise_gradient_table_types(table)
        self.assertEqual(result[0]["Time"], 0.0)
        self.assertEqual(result[0]["CompositionA"], 10.0)
        self.assertEqual(result[0]["Curve"], 0)
        self.assertEqual(result[1]["Time"], 5.0)
        self.assertEqual(result[1]["CompositionA"], 15.0)
        self.assertEqual(result[1]["Curve"], 1)
        self.assertEqual(result[2]["Time"], 10.0)
        self.assertEqual(result[2]["CompositionA"], 20.0)
        self.assertEqual(result[2]["Curve"], 6)

    def test_standardises_types_with_multiple_keys(self):
        table = [
            {
                "Time": "Initial",
                "CompositionA": "10",
                "CompositionB": "20",
                "Curve": "Initial",
            },
            {"Time": "5", "CompositionA": "15.5", "CompositionB": "25.5", "Curve": "1"},
        ]
        result = standardise_gradient_table_types(table)
        self.assertEqual(result[0]["Time"], 0.0)
        self.assertEqual(result[0]["CompositionA"], 10.0)
        self.assertEqual(result[0]["CompositionB"], 20.0)
        self.assertEqual(result[0]["Curve"], 0)
        self.assertEqual(result[1]["Time"], 5.0)
        self.assertEqual(result[1]["CompositionA"], 15.5)
        self.assertEqual(result[1]["CompositionB"], 25.5)
        self.assertEqual(result[1]["Curve"], 1)


if __name__ == "__main__":
    unittest.main()
