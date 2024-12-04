import json
import os
import unittest

from OptiHPLCHandler.applications.method_converter.method_converter import (
    change_gradient_table,
)


def get_example_file_dict() -> dict:
    """
    Get an example file from the empower_method_examples folder.

    :param file_name: The name of the example file.
    """
    example = {}
    example_folder = os.path.join("tests", "empower_method_examples")
    example_files = os.listdir(example_folder)
    json_file_list = [file for file in example_files if ".json" in file]
    for file in json_file_list:
        file_path = os.path.join(example_folder, file)
        with open(file_path) as f:
            example[file] = json.load(f)
    return example


class TestChangeGradient(unittest.TestCase):
    def setUp(self) -> None:
        self.bsm_grad1 = [
            {
                "Time": "Initial",
                "Flow": "0.600",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "Initial",
            },
            {
                "Time": "1.00",
                "Flow": "0.600",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": "6",
            },
        ]
        self.bsm_grad2 = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "70.0",
                "CompositionB": "30.0",
                "Curve": "Initial",
            },
            {
                "Time": "1.00",
                "Flow": "0.500",
                "CompositionA": "30.0",
                "CompositionB": "70.0",
                "Curve": "6",
            },
        ]
        self.bsm_iso = [
            {
                "Time": "Initial",
                "Flow": "0.600",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "Initial",
            },
        ]
        self.bsm_iso2 = [
            {
                "Time": "Initial",
                "Flow": "0.600",
                "CompositionA": "80.0",
                "CompositionB": "20.0",
                "Curve": "Initial",
            },
        ]
        self.qsm_iso = [
            {
                "Time": "Initial",
                "Flow": "0.600",
                "CompositionA": "80.0",
                "CompositionB": "20.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": "Initial",
            },
        ]
        self.qsm_iso2 = [
            {
                "Time": "Initial",
                "Flow": "0.600",
                "CompositionC": "70.0",
                "CompositionD": "30.0",
                "CompositionA": "0.0",
                "CompositionB": "0.0",
                "Curve": "Initial",
            },
        ]
        self.qsm_iso3 = [
            {
                "Time": "Initial",
                "Flow": "0.600",
                "CompositionC": "70.0",
                "CompositionB": "30.0",
                "CompositionA": "0.0",
                "CompositionD": "0.0",
                "Curve": "Initial",
            },
        ]

        self.qsm_iso_threecomp = [
            {
                "Time": "Initial",
                "Flow": "0.600",
                "CompositionA": "80.0",
                "CompositionB": "10.0",
                "CompositionC": "10.0",
                "CompositionD": "0.0",
                "Curve": "Initial",
            },
        ]
        self.qsm_grad_ab = [
            {
                "Time": "Initial",
                "Flow": "0.600",
                "CompositionA": "80.0",
                "CompositionB": "20.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": "Initial",
            },
            {
                "Time": "1.00",
                "Flow": "0.600",
                "CompositionA": "20.0",
                "CompositionB": "80.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": "6",
            },
        ]
        self.qsm_grad_cd = [
            {
                "Time": "Initial",
                "Flow": "0.600",
                "CompositionC": "70.0",
                "CompositionD": "30.0",
                "CompositionA": "0.0",
                "CompositionB": "0.0",
                "Curve": "Initial",
            },
            {
                "Time": "1.00",
                "Flow": "0.600",
                "CompositionC": "30.0",
                "CompositionD": "70.0",
                "CompositionA": "0.0",
                "CompositionB": "0.0",
                "Curve": "6",
            },
        ]

    def test_bsm_to_bsm(self) -> None:
        """Test change_gradient_table function for BSM to BSM
        Notes:
        Transfers gradient 2 to the format of gradient 1 and checks if the output is the
        same as gradient 1.
        """
        # Check input
        self.assertEqual(self.bsm_grad2[0]["CompositionA"], "70.0")
        self.assertEqual(self.bsm_grad1[0]["CompositionA"], "90.0")

        # Run function
        new_gradient_table = change_gradient_table(self.bsm_grad2, self.bsm_grad1)

        # Check output
        for grad1, grad2 in zip(self.bsm_grad2, new_gradient_table):
            self.assertEqual(grad1, grad2)

    def test_bsm_to_qsm(self) -> None:
        """Test change_gradient_table function for BSM to QSM
        Notes:
        Transfers gradient 1 to the format of qsm_grad_ab and checks if the output is
        the same as qsm_grad_ab.
        """
        # Check input
        self.assertEqual(self.bsm_grad1[0]["CompositionA"], "90.0")
        self.assertEqual(self.qsm_grad_ab[0]["CompositionA"], "80.0")
        self.assertTrue("CompositionC" in self.qsm_grad_ab[0])
        self.assertTrue("CompositionD" in self.qsm_grad_ab[0])
        self.assertFalse("CompositionC" in self.bsm_grad1[0])
        self.assertFalse("CompositionD" in self.bsm_grad1[0])

        # Run function
        new_gradient_table = change_gradient_table(
            self.bsm_grad1,
            self.qsm_grad_ab,
        )

        # Check output
        for grad1, grad2 in zip(self.bsm_grad1, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])
            self.assertTrue("CompositionC" in grad2)
            self.assertTrue("CompositionD" in grad2)

    def test_qsm_to_bsm(self) -> None:
        """Test change_gradient_table function for QSM to BSM
        Notes:
        Transfers gradient ab to the format of bsm_grad1 and checks if the output is the
        same as bsm_grad1.
        """
        # Check input
        self.assertEqual(self.qsm_grad_ab[0]["CompositionA"], "80.0")
        self.assertEqual(self.bsm_grad1[0]["CompositionA"], "90.0")
        self.assertTrue("CompositionC" in self.qsm_grad_ab[0])
        self.assertTrue("CompositionD" in self.qsm_grad_ab[0])
        self.assertFalse("CompositionC" in self.bsm_grad1[0])
        self.assertFalse("CompositionD" in self.bsm_grad1[0])

        # Run function
        new_gradient_table = change_gradient_table(
            self.qsm_grad_ab,
            self.bsm_grad1,
        )

        # Check output
        for grad1, grad2 in zip(self.qsm_grad_ab, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])
            self.assertFalse("CompositionC" in grad2)
            self.assertFalse("CompositionD" in grad2)

    def test_qsm_to_qsm(self) -> None:
        """Test change_gradient_table function for QSM to QSM
        Notes:
        Transfers gradient cd to the format of qsm_grad_ab and checks if the output is
        the same as qsm_grad_ab.
        """
        # Check input
        self.assertEqual(self.qsm_grad_cd[0]["CompositionC"], "70.0")
        self.assertEqual(self.qsm_grad_ab[0]["CompositionA"], "80.0")
        self.assertTrue("CompositionC" in self.qsm_grad_cd[0])
        self.assertTrue("CompositionD" in self.qsm_grad_cd[0])
        self.assertTrue("CompositionC" in self.qsm_grad_ab[0])
        self.assertTrue("CompositionD" in self.qsm_grad_ab[0])

        # Run function
        new_gradient_table = change_gradient_table(
            self.qsm_grad_cd,
            self.qsm_grad_ab,
        )

        # Check output
        self.assertEqual(self.qsm_grad_cd, new_gradient_table)

    def test_bsm_to_bsm_iso(self) -> None:
        """Test change_gradient_table function for BSM to BSM"""
        # Check input
        self.assertEqual(self.bsm_iso2[0]["CompositionA"], "80.0")  # BSM Isocratic
        self.assertEqual(self.bsm_grad1[0]["CompositionA"], "90.0")  # BSM Gradient

        # Run function
        new_gradient_table = change_gradient_table(
            self.bsm_iso2,
            self.bsm_grad1,
        )

        # Check output
        self.assertEqual(self.bsm_iso2, new_gradient_table)

    def test_bsm_to_qsm_iso(self) -> None:
        """Test change_gradient_table function for BSM to QSM"""
        # Check input
        self.assertEqual(self.bsm_iso[0]["CompositionA"], "90.0")
        self.assertEqual(self.qsm_iso[0]["CompositionA"], "80.0")

        # Run function
        new_gradient_table = change_gradient_table(
            self.bsm_iso,
            self.qsm_iso,
        )

        # Check output
        # Cant compare the gradient tables directly because of the difference in
        # compositions
        for grad1, grad2 in zip(self.bsm_iso, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])

    def test_qsmab_to_bsm_iso(self) -> None:
        """Test change_gradient_table function for QSM to BSM."""
        # Check input
        self.assertEqual(self.qsm_iso[0]["CompositionA"], "80.0")
        self.assertEqual(self.bsm_iso[0]["CompositionA"], "90.0")

        # Run function
        new_gradient_table = change_gradient_table(
            self.qsm_iso,
            self.bsm_iso,
        )

        # Check output
        for grad1, grad2 in zip(self.qsm_iso, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])

    def test_qsmcd_to_bsm_iso(self) -> None:
        """Test change_gradient_table function for QSM to BSM. The QSM uses CompositionC
        and CompositionD, while the BSM uses CompositionA and CompositionB. Thus the
        CompositionC and CompositionD values are transferred to CompositionB and
        CompositionA, respectively."""
        # Check input
        self.assertEqual(self.qsm_iso2[0]["CompositionC"], "70.0")
        self.assertEqual(self.bsm_iso[0]["CompositionA"], "90.0")

        # Run function
        new_gradient_table = change_gradient_table(
            self.qsm_iso2,
            self.bsm_iso,
        )

        # Check output
        for grad1, grad2 in zip(self.qsm_iso2, new_gradient_table):
            self.assertEqual(grad1["CompositionC"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionD"], grad2["CompositionB"])

    def test_qsmcb_to_bsm_iso(self) -> None:
        """Test change_gradient_table function for QSM to BSM. The QSM uses CompositionC
        and CompositionD, while the BSM uses CompositionA and CompositionB. Thus the
        CompositionC and CompositionD values are transferred to CompositionB and
        CompositionA, respectively."""
        # Check input
        self.assertEqual(self.qsm_iso3[0]["CompositionC"], "70.0")
        self.assertEqual(self.bsm_iso[0]["CompositionA"], "90.0")

        # Run function
        new_gradient_table = change_gradient_table(
            self.qsm_iso3,
            self.bsm_iso,
        )

        # Check output
        for grad1, grad2 in zip(self.qsm_iso3, new_gradient_table):
            self.assertEqual(grad1["CompositionC"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])

    def test_qsm_to_qsm_iso(self) -> None:
        """Test change_gradient_table function for QSM to QSM."""
        # Check input
        self.assertEqual(self.qsm_iso2[0]["CompositionC"], "70.0")
        self.assertEqual(self.qsm_iso[0]["CompositionA"], "80.0")

        # Run function
        new_gradient_table = change_gradient_table(
            self.qsm_iso,
            self.qsm_iso2,
        )

        # Check output
        self.assertEqual(self.qsm_iso, new_gradient_table)

    def test_qsm3_to_qsm_iso(self) -> None:
        """Test change_gradient_table function for QSM to QSM. The input QSM uses
        three components, while the output QSM uses two components. The output should be
        the same as the input."""
        # Check input
        self.assertEqual(self.qsm_iso_threecomp[0]["CompositionC"], "10.0")
        self.assertEqual(self.qsm_iso_threecomp[0]["CompositionD"], "0.0")
        self.assertEqual(self.qsm_iso_threecomp[0]["CompositionA"], "80.0")
        self.assertEqual(self.qsm_iso_threecomp[0]["CompositionB"], "10.0")

        # Run function
        new_gradient_table = change_gradient_table(
            self.qsm_iso_threecomp,
            self.qsm_iso,
        )

        # Check output
        self.assertEqual(self.qsm_iso_threecomp, new_gradient_table)
