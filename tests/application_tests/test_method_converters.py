import json
import os
import unittest
from typing import Union

from OptiHPLCHandler.applications.method_converter.method_converter import (
    MethodParts,
    change_gradient_table,
    change_wavelengths,
    transfer_method_from_method_parts,
)
from OptiHPLCHandler.empower_detector_module_method import PDAMethod, TUVMethod
from OptiHPLCHandler.empower_instrument_method import EmpowerInstrumentMethod


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


class TestMethodPartsInitialisation(unittest.TestCase):
    def setUp(self):
        self.example = get_example_file_dict()
        self.qsm_method = EmpowerInstrumentMethod(
            self.example["response-QSM-PDA-Acq.json"]
        )

        self.bsm_tuv_method = EmpowerInstrumentMethod(
            self.example["response-BSM-TUV-CM-Acq.json"]
        )

    def test_extract_method_parts(self):
        data_extracted = MethodParts(self.bsm_tuv_method)
        detector: Union[
            PDAMethod, TUVMethod
        ] = self.bsm_tuv_method.detector_method_list[0]

        self.assertIsInstance(data_extracted, MethodParts)
        self.assertEqual(
            data_extracted.gradient_table, self.bsm_tuv_method.gradient_table
        )
        self.assertEqual(
            data_extracted.channel_dict,
            detector.channel_dict,
        )
        self.assertEqual(
            data_extracted.sample_temperature, self.bsm_tuv_method.sample_temperature
        )
        self.assertEqual(
            data_extracted.column_temperature, self.bsm_tuv_method.column_temperature
        )
        self.assertEqual(
            data_extracted.original_method_name, self.bsm_tuv_method.method_name
        )


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
        for grad1, grad2 in zip(self.qsm_grad_cd, new_gradient_table):
            self.assertEqual(grad1["CompositionC"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionD"], grad2["CompositionB"])

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
        for grad1, grad2 in zip(self.bsm_iso2, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])

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
        for grad1, grad2 in zip(self.bsm_iso, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])
            self.assertEqual(grad2["CompositionC"], "0.0")
            self.assertEqual(grad2["CompositionD"], "0.0")

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
        for grad1, grad2 in zip(self.qsm_iso, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])
            self.assertEqual(grad1["CompositionC"], grad2["CompositionC"])
            self.assertEqual(grad1["CompositionD"], grad2["CompositionD"])

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
        for grad1, grad2 in zip(self.qsm_iso_threecomp, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])
            self.assertEqual(grad1["CompositionC"], grad2["CompositionC"])
            self.assertEqual(grad1["CompositionD"], grad2["CompositionD"])


class TestChangeWavelengths(unittest.TestCase):
    def setUp(self):
        self.pda = {
            "Channel1": {"Wavelength1": 210.0, "Enable": True},
            "Channel2": {"Wavelength1": 220.0, "Enable": True},
            "Channel3": {"Wavelength1": 230.0, "Enable": False},
            "Channel4": {"Wavelength1": 240.0, "Enable": False},
            "Channel5": {"Wavelength1": 250.0, "Enable": False},
            "Channel6": {"Wavelength1": 260.0, "Enable": False},
            "Channel7": {"Wavelength1": 270.0, "Enable": False},
            "Channel8": {"Wavelength1": 280.0, "Enable": False},
        }
        self.pda1 = {
            "Channel1": {"Wavelength1": 110.0, "Enable": True},
            "Channel2": {"Wavelength1": 120.0, "Enable": False},
            "Channel3": {"Wavelength1": 130.0, "Enable": False},
            "Channel4": {"Wavelength1": 140.0, "Enable": False},
            "Channel5": {"Wavelength1": 150.0, "Enable": False},
            "Channel6": {"Wavelength1": 160.0, "Enable": False},
            "Channel7": {"Wavelength1": 170.0, "Enable": False},
            "Channel8": {"Wavelength1": 180.0, "Enable": False},
        }

        self.tuv = {
            "Channel1": {"Wavelength": 310.0},
            "Channel2": {"Wavelength": 320.0},
        }
        self.tuv1 = {
            "Channel1": {"Wavelength": 410.0},
            "Channel2": {"Wavelength": 420.0},
        }

    def test_pda_to_pda(self):
        """Test change_wavelengths function for PDA to PDA
        Notes:
        - Modifies the pda1 in place
        - change the wavelengths of the pda dictionary to match the pda1 dictionary
        - the pda1 should have the same wavelengths as the pda dictionary
        - the enabled keys should be the same as the pda dictionary
        """
        # Check input
        self.assertEqual(self.pda["Channel1"]["Wavelength1"], 210.0)
        self.assertEqual(self.pda1["Channel1"]["Wavelength1"], 110.0)
        self.assertTrue(self.pda["Channel1"]["Enable"])
        self.assertTrue(self.pda1["Channel1"]["Enable"])

        # Run function
        change_wavelengths(self.pda, self.pda1)

        # Check output
        for value_pda, value_pda1 in zip(self.pda.values(), self.pda1.values()):
            self.assertEqual(
                value_pda.get("Wavelength1"),
                value_pda1.get("Wavelength1"),
            )
            self.assertEqual(value_pda.get("Enable"), value_pda1.get("Enable"))

    def test_pda_to_tuv(self):
        """Test change_wavelengths function for PDA to TUV
        Notes:
        - Modifies the tuv in place
        - change the wavelengths of the pda dictionary to match the tuv dictionary
        - the tuv should have the same wavelengths as the pda dictionary
        """
        # Check input
        self.assertEqual(self.pda["Channel1"]["Wavelength1"], 210.0)
        self.assertEqual(self.tuv["Channel1"]["Wavelength"], 310.0)

        # Run function
        change_wavelengths(self.pda, self.tuv)

        # Check output
        for value_pda, value_tuv in zip(self.pda.values(), self.tuv.values()):
            self.assertEqual(
                value_pda.get("Wavelength1"),
                value_tuv.get("Wavelength"),
            )

    def test_tuv_to_pda(self):
        """Test change_wavelengths function for TUV to PDA
        Notes:
        - Modifies the pda in place
        - change the wavelengths of the tuv dictionary to match the pda dictionary
        - the pda should have the same wavelengths as the tuv dictionary
        """
        # Check input
        self.assertEqual(self.tuv["Channel1"]["Wavelength"], 310.0)
        self.assertEqual(self.pda["Channel1"]["Wavelength1"], 210.0)

        # Run function
        change_wavelengths(self.tuv, self.pda)

        # Check output
        for value_tuv, value_pda in zip(self.tuv.values(), self.pda.values()):
            self.assertEqual(
                value_tuv.get("Wavelength"),
                value_pda.get("Wavelength1"),
            )

    def test_tuv_to_tuv(self):
        """Test change_wavelengths function for TUV to TUV
        Notes:
        - Modifies the tuv1 in place
        - change the wavelengths of the tuv dictionary to match the tuv1 dictionary
        - the tuv1 should have the same wavelengths as the tuv dictionary
        """
        # Check input
        self.assertEqual(self.tuv["Channel1"]["Wavelength"], 310.0)
        self.assertEqual(self.tuv1["Channel1"]["Wavelength"], 410.0)

        # Run function
        change_wavelengths(self.tuv, self.tuv1)

        # Check output
        for value_tuv, value_tuv1 in zip(self.tuv.values(), self.tuv1.values()):
            self.assertEqual(
                value_tuv.get("Wavelength"),
                value_tuv1.get("Wavelength"),
            )


class TestTransferMethodFromParts(unittest.TestCase):
    def setUp(self):
        self.example = get_example_file_dict()
        self.qsm_method = EmpowerInstrumentMethod(
            self.example["response-QSM-PDA-Acq.json"]
        )

        self.bsm_tuv_method = EmpowerInstrumentMethod(
            self.example["response-BSM-TUV-CM-Acq.json"]
        )
        self.qsm_gradient_table = [
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
        self.bsm_gradient_table = [
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
        self.bsm_tuv_method.gradient_table = self.bsm_gradient_table
        self.qsm_method.gradient_table = self.qsm_gradient_table

    def test_transfer_method_from_parts(self):
        parts_from_input = MethodParts(self.bsm_tuv_method)

        # Check extracted parts
        self.assertEqual(
            parts_from_input.gradient_table, self.bsm_tuv_method.gradient_table
        )
        self.assertEqual(
            parts_from_input.channel_dict["Channel1"]["Wavelength"],
            self.bsm_tuv_method.detector_method_list[0].channel_dict["Channel1"][
                "Wavelength"
            ],
        )
        self.assertEqual(
            parts_from_input.sample_temperature,
            self.bsm_tuv_method.sample_temperature,
        )
        self.assertEqual(
            parts_from_input.column_temperature,
            self.bsm_tuv_method.column_temperature,
        )
        self.assertEqual(
            parts_from_input.solvent_lines,
            self.bsm_tuv_method.solvent_handler_method.solvent_lines,
        )
        self.assertEqual(
            parts_from_input.original_method_name, self.bsm_tuv_method.method_name
        )

        # Check transferred method
        transfer_method_from_method_parts(parts_from_input, self.qsm_method)

        # Gradient
        for grad1, grad2 in zip(
            self.bsm_tuv_method.gradient_table, self.qsm_method.gradient_table
        ):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])
            self.assertTrue("CompositionC" in grad2)
            self.assertTrue("CompositionD" in grad2)

        # Detector
        for value1, value2 in zip(
            self.bsm_tuv_method.detector_method_list[0].channel_dict.values(),
            self.qsm_method.detector_method_list[0].channel_dict.values(),
        ):
            self.assertEqual(value1["Wavelength"], value2["Wavelength1"])

        # Sample temperature
        self.assertEqual(
            self.bsm_tuv_method.sample_temperature, self.qsm_method.sample_temperature
        )

        # Column temperature
        self.assertEqual(
            self.bsm_tuv_method.column_temperature, self.qsm_method.column_temperature
        )

        # Name alteration
        self.assertEqual(self.qsm_method.method_name[-9:], "_transfer")
