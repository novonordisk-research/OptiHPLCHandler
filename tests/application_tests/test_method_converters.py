import json
import os
import unittest
from typing import Union

from OptiHPLCHandler.applications.method_converter.method_converter import (
    change_gradient_table,
    change_wavelengths,
    transfer_gradient_table,
    transfer_wavelengths,
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


class TestChangeGradient(unittest.TestCase):
    def setUp(self) -> None:
        self.bsm_grad1 = [
            {
                "Time": "0.00",
                "Flow": "0.600",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "6",
            },
            {
                "Time": "1.00",
                "Flow": "0.600",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": "6",
            },
        ]
        self.bsm_grad1_lines = ["A1", "B1"]
        self.bsm_grad2 = [
            {
                "Time": "0.00",
                "Flow": "0.500",
                "CompositionA": "70.0",
                "CompositionB": "30.0",
                "Curve": "6",
            },
            {
                "Time": "1.00",
                "Flow": "0.500",
                "CompositionA": "30.0",
                "CompositionB": "70.0",
                "Curve": "6",
            },
        ]
        self.bsm_grad2_lines = ["A2", "B2"]
        self.bsm_iso = [
            {
                "Time": "0.00",
                "Flow": "0.600",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "6",
            },
        ]
        self.bsm_iso_lines = ["A1", "B1"]
        self.qsm_grad_ab = [
            {
                "Time": "0.00",
                "Flow": "0.600",
                "CompositionA": "80.0",
                "CompositionB": "20.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": "6",
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
        self.qsm_grad_ab_lines = ["A", "B", "C", "D1"]
        self.qsm_grad_cd = [
            {
                "Time": "0.00",
                "Flow": "0.600",
                "CompositionC": "70.0",
                "CompositionD": "30.0",
                "CompositionA": "0.0",
                "CompositionB": "0.0",
                "Curve": "6",
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
        self.qsm_grad_cd_lines = ["A", "B", "C", "D2"]

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
        new_gradient_table = change_gradient_table(
            self.bsm_grad2, self.bsm_grad1, self.bsm_grad1_lines
        )

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

        # Run function
        new_gradient_table = change_gradient_table(
            self.bsm_grad1, self.qsm_grad_ab, self.qsm_grad_ab_lines
        )

        # Check output
        for grad1, grad2 in zip(self.bsm_grad1, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])

    def test_qsm_to_bsm(self) -> None:
        """Test change_gradient_table function for QSM to BSM
        Notes:
        Transfers gradient ab to the format of bsm_grad1 and checks if the output is the
        same as bsm_grad1.
        """
        # Check input
        self.assertEqual(self.qsm_grad_ab[0]["CompositionA"], "80.0")
        self.assertEqual(self.bsm_grad1[0]["CompositionA"], "90.0")

        # Run function
        new_gradient_table = change_gradient_table(
            self.qsm_grad_ab, self.bsm_grad1, self.bsm_grad1_lines
        )

        # Check output
        for grad1, grad2 in zip(self.qsm_grad_ab, new_gradient_table):
            self.assertEqual(grad1["CompositionA"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionB"], grad2["CompositionB"])

    def test_qsm_to_qsm(self) -> None:
        """Test change_gradient_table function for QSM to QSM
        Notes:
        Transfers gradient cd to the format of qsm_grad_ab and checks if the output is
        the same as qsm_grad_ab.
        """
        # Check input
        self.assertEqual(self.qsm_grad_cd[0]["CompositionC"], "70.0")
        self.assertEqual(self.qsm_grad_ab[0]["CompositionA"], "80.0")

        # Run function
        new_gradient_table = change_gradient_table(
            self.qsm_grad_cd, self.qsm_grad_ab, self.qsm_grad_ab_lines
        )

        # Check output
        for grad1, grad2 in zip(self.qsm_grad_cd, new_gradient_table):
            self.assertEqual(grad1["CompositionC"], grad2["CompositionA"])
            self.assertEqual(grad1["CompositionD"], grad2["CompositionB"])


class TestTransferGradient(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()
        self.bsm_tuv_method = EmpowerInstrumentMethod(
            self.example["response-BSM-TUV-CM-Acq.json"]
        )
        self.bsm_pda_method = EmpowerInstrumentMethod(
            self.example["response-BSM-PDA-Acq.json"]
        )
        self.qsm_method = EmpowerInstrumentMethod(
            self.example["response-QSM-2489-Acq.json"]
        )

        bsm_grad1 = [
            {
                "Time": "0.00",
                "Flow": "0.600",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "6",
            },
            {
                "Time": "1.00",
                "Flow": "0.600",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": "6",
            },
        ]
        bsm_grad2 = [
            {
                "Time": "0.00",
                "Flow": "0.500",
                "CompositionA": "70.0",
                "CompositionB": "30.0",
                "Curve": "6",
            },
            {
                "Time": "1.00",
                "Flow": "0.500",
                "CompositionA": "30.0",
                "CompositionB": "70.0",
                "Curve": "6",
            },
        ]
        bsm_iso = [
            {
                "Time": "0.00",
                "Flow": "0.600",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "6",
            },
        ]
        qsm_grad_ab = [
            {
                "Time": "0.00",
                "Flow": "0.600",
                "CompositionA": "80.0",
                "CompositionB": "20.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": "6",
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
        qsm_grad_cd = [
            {
                "Time": "0.00",
                "Flow": "0.600",
                "CompositionC": "70.0",
                "CompositionD": "30.0",
                "CompositionA": "0.0",
                "CompositionB": "0.0",
                "Curve": "6",
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

        # Modified Methods
        self.bsm1_tuv = self.bsm_tuv_method.copy()
        self.bsm1_tuv.gradient_table = bsm_grad1

        self.bsm2_tuv = self.bsm_tuv_method.copy()
        self.bsm2_tuv.gradient_table = bsm_grad2

        self.bsm1_pda = self.bsm_pda_method.copy()
        self.bsm1_pda.gradient_table = bsm_grad1

        self.bsm2_pda = self.bsm_pda_method.copy()
        self.bsm2_pda.gradient_table = bsm_grad2

        self.qsm_ab = self.qsm_method.copy()
        self.qsm_ab.gradient_table = qsm_grad_ab

        self.qsm_cd = self.qsm_method.copy()
        self.qsm_cd.gradient_table = qsm_grad_cd

        self.bsm_tuv_iso = self.bsm_tuv_method.copy()
        self.bsm_tuv_iso.gradient_table = bsm_iso

    def test_instrument_method(self):
        self.assertIsInstance(self.bsm_tuv_method, EmpowerInstrumentMethod)
        self.assertIsInstance(self.bsm_pda_method, EmpowerInstrumentMethod)
        self.assertIsInstance(self.qsm_method, EmpowerInstrumentMethod)

    def test_bsm_to_qsm(self):
        """Test transfer_gradient_table function for BSM to QSM
        Notes:
        - Modifies the qsm_mock in place
        - transfer gradient starting at 90% CompositionA and 10% CompositionB in a bsm
        to a qsm (with 80% CompositionA and 20% CompositionB initially)
        - the qsm should have 90% CompositionA and 10% CompositionB after the transfer
        - there should be CompositionA, B, C, and D in the qsm gradient table
        """
        # Check input
        self.assertEqual(self.bsm1_tuv.gradient_table[0]["CompositionA"], "90.0")
        self.assertEqual(self.qsm_ab.gradient_table[0]["CompositionA"], "80.0")

        # Run function
        transfer_gradient_table(self.bsm1_tuv, self.qsm_ab)

        # Check output
        self.assertEqual(self.qsm_ab.gradient_table[0]["CompositionA"], "90.0")
        self.assertTrue("CompositionB" in self.qsm_ab.gradient_table[0])
        self.assertTrue("CompositionC" in self.qsm_ab.gradient_table[0])
        self.assertTrue("CompositionD" in self.qsm_ab.gradient_table[0])

    def test_qsm_to_bsm(self):
        """Test transfer_gradient_table function for QSM to BSM
        Notes:
        - Modifies the bsm_mock in place
        - transfer gradient starting at 80% CompositionA and 20% CompositionB in a qsm
        to a bsm (with 90% CompositionA and 10% CompositionB initially)
        - the bsm should have 80% CompositionA and 20% CompositionB after the transfer
        - there should be no CompositionC and CompositionD in the bsm gradient table
        """
        # Check input
        self.assertEqual(self.bsm1_tuv.gradient_table[0]["CompositionA"], "90.0")
        self.assertEqual(self.qsm_ab.gradient_table[0]["CompositionA"], "80.0")

        # Run function
        transfer_gradient_table(self.qsm_ab, self.bsm1_tuv)

        # Check output
        self.assertEqual(self.bsm1_tuv.gradient_table[0]["CompositionA"], "80.0")
        self.assertTrue("CompositionB" in self.qsm_ab.gradient_table[0])
        self.assertFalse("CompositionC" in self.bsm1_tuv.gradient_table[0])
        self.assertFalse("CompositionD" in self.bsm1_tuv.gradient_table[0])

    def test_bsm_to_bsm(self):
        """Test transfer_gradient_table function for BSM to BSM
        Notes:
        - Modifies the bsm_mock_2 in place
        - transfer gradient starting at 70% CompositionA and 30% CompositionB in a bsm
        to another bsm (with 90% CompositionA and 10% CompositionB initially)
        - the bsm should have 70% CompositionA and 30% CompositionB after the transfer
        - there should be no CompositionC and CompositionD in the bsm gradient table
        """

        # Check input
        self.assertEqual(self.bsm1_tuv.gradient_table[0]["CompositionA"], "90.0")
        self.assertEqual(self.bsm2_tuv.gradient_table[0]["CompositionA"], "70.0")

        # Run function
        transfer_gradient_table(self.bsm1_tuv, self.bsm2_tuv)

        # Check output
        self.assertEqual(self.bsm2_tuv.gradient_table[0]["CompositionA"], "90.0")
        self.assertTrue("CompositionB" in self.bsm2_tuv.gradient_table[0])
        self.assertFalse("CompositionC" in self.bsm2_tuv.gradient_table[0])
        self.assertFalse("CompositionD" in self.bsm2_tuv.gradient_table[0])

    def test_qsm_to_qsm(self):
        """Test transfer_gradient_table function for QSM to QSM
        Notes:
        - Modifies the qsm_mock_2 in place
        - transfer gradient starting at 70% CompositionC and 30% CompositionD in a qsm
        to another qsm (with 80% CompositionA and 20% CompositionB initially)
        - the qsm should have 70% CompositionC and 30% CompositionD after the transfer
        - there should be CompositionA, B, C, and D in the qsm gradient table
        """
        # Check input
        self.assertEqual(self.qsm_ab.gradient_table[0]["CompositionA"], "80.0")
        self.assertEqual(self.qsm_cd.gradient_table[0]["CompositionC"], "70.0")

        # Run function
        transfer_gradient_table(self.qsm_ab, self.qsm_cd)

        # Check output
        self.assertEqual(self.qsm_cd.gradient_table[0]["CompositionC"], "80.0")
        self.assertTrue("CompositionA" in self.qsm_cd.gradient_table[0])
        self.assertTrue("CompositionB" in self.qsm_cd.gradient_table[0])
        self.assertTrue("CompositionD" in self.qsm_cd.gradient_table[0])

    def test_qsm_compcd_to_bsm_compab(self):
        """Test transfer_gradient_table function for QSM to BSM
        Notes:
        - Modifies the bsm_mock in place
        - transfer gradient starting at 70% CompositionC and 30% CompositionD in a qsm
        to a bsm (with 90% CompositionA and 10% CompositionB initially)
        - the bsm should have 70% CompositionA and 30% CompositionB after the transfer
        - there should be no CompositionC and CompositionD in the bsm gradient table
        """
        # Check input
        self.assertEqual(self.bsm1_tuv.gradient_table[0]["CompositionA"], "90.0")
        self.assertEqual(self.qsm_cd.gradient_table[0]["CompositionC"], "70.0")

        # Run function
        transfer_gradient_table(self.qsm_cd, self.bsm1_tuv)

        # Check output
        self.assertEqual(self.bsm1_tuv.gradient_table[0]["CompositionA"], "70.0")
        self.assertEqual(self.bsm1_tuv.gradient_table[0]["CompositionB"], "30.0")
        self.assertFalse("CompositionC" in self.bsm1_tuv.gradient_table[0])
        self.assertFalse("CompositionD" in self.bsm1_tuv.gradient_table[0])

    def test_isocratic_input(self):
        # Check input
        self.assertEqual(self.bsm_tuv_iso.gradient_table[0]["CompositionA"], "90.0")
        self.assertEqual(self.qsm_ab.gradient_table[0]["CompositionA"], "80.0")
        self.assertEqual(len(self.bsm_tuv_iso.gradient_table), 1)

        # Run function
        with self.assertRaises(NotImplementedError):
            transfer_gradient_table(self.bsm_tuv_iso, self.qsm_ab)


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


class TestTransferWavelength(unittest.TestCase):
    def setUp(self):
        self.example = get_example_file_dict()
        self.bsm_tuv_method = EmpowerInstrumentMethod(
            self.example["response-BSM-TUV-CM-Acq.json"]
        )
        self.bsm_pda_method = EmpowerInstrumentMethod(
            self.example["response-BSM-PDA-Acq.json"]
        )

        self.channel_dict_pda = {
            "Channel1": {"Wavelength1": 210.0, "Enable": True},
            "Channel2": {"Wavelength1": 220.0, "Enable": True},
            "Channel3": {"Wavelength1": 230.0, "Enable": False},
            "Channel4": {"Wavelength1": 240.0, "Enable": False},
            "Channel5": {"Wavelength1": 250.0, "Enable": False},
            "Channel6": {"Wavelength1": 260.0, "Enable": False},
            "Channel7": {"Wavelength1": 270.0, "Enable": False},
            "Channel8": {"Wavelength1": 280.0, "Enable": False},
        }

        self.channel_dict_pda1 = {
            "Channel1": {"Wavelength1": 310.0, "Enable": True},
            "Channel2": {"Wavelength1": 320.0, "Enable": True},
            "Channel3": {"Wavelength1": 330.0, "Enable": False},
            "Channel4": {"Wavelength1": 340.0, "Enable": False},
            "Channel5": {"Wavelength1": 350.0, "Enable": False},
            "Channel6": {"Wavelength1": 360.0, "Enable": False},
            "Channel7": {"Wavelength1": 370.0, "Enable": False},
            "Channel8": {"Wavelength1": 380.0, "Enable": False},
        }

        self.channel_dict_tuv = {
            "Channel1": {"Wavelength": 310.0},
            "Channel2": {"Wavelength": 320.0},
        }
        self.channel_dict_tuv1 = {
            "Channel1": {"Wavelength": 410.0},
            "Channel2": {"Wavelength": 420.0},
        }

        # Modified Methods
        # TUV
        self.tuv: EmpowerInstrumentMethod = self.bsm_tuv_method.copy()
        self.tuv_detector: Union[PDAMethod, TUVMethod] = self.tuv.detector_method_list[
            0
        ]
        self.tuv_detector.channel_dict = self.channel_dict_tuv

        # TUV1
        self.tuv1: EmpowerInstrumentMethod = self.bsm_tuv_method.copy()
        self.tuv1_detector: Union[PDAMethod, TUVMethod] = (
            self.tuv1.detector_method_list[0]
        )
        self.tuv1_detector.channel_dict = self.channel_dict_tuv1

        # PDA
        self.pda: EmpowerInstrumentMethod = self.bsm_pda_method.copy()
        self.pda_detector: Union[PDAMethod, TUVMethod] = self.pda.detector_method_list[
            0
        ]
        self.pda_detector.channel_dict = self.channel_dict_pda

        # PDA1
        self.pda1: EmpowerInstrumentMethod = self.bsm_pda_method.copy()
        self.pda1_detector: Union[PDAMethod, TUVMethod] = (
            self.pda1.detector_method_list[0]
        )
        self.pda1_detector.channel_dict = self.channel_dict_pda1

    def test_instrument_method(self):
        self.assertIsInstance(self.tuv, EmpowerInstrumentMethod)
        self.assertIsInstance(self.tuv1, EmpowerInstrumentMethod)
        self.assertIsInstance(self.pda, EmpowerInstrumentMethod)
        self.assertIsInstance(self.pda1, EmpowerInstrumentMethod)

    def test_pda_to_pda(self):
        """Test transfer_wavelengths function for PDA to PDA
        Notes:
        - Modifies the pda1 in place
        - transfer the wavelengths of the pda detector to the pda1 detector
        - the pda1 detector should have the same wavelengths as the pda detector
        """
        # Check input
        self.assertEqual(
            self.pda_detector.channel_dict["Channel1"]["Wavelength1"], "210.0"
        )
        self.assertEqual(
            self.pda1_detector.channel_dict["Channel1"]["Wavelength1"], "310.0"
        )
        self.assertTrue(self.pda_detector.channel_dict["Channel1"]["Enable"])
        self.assertTrue(self.pda1_detector.channel_dict["Channel1"]["Enable"])

        # Run function
        transfer_wavelengths(self.pda, self.pda1)

        # Check output
        # iterate through the shortest channel_dict checking if the wavelengths
        for value_pda, value_pda1 in zip(
            self.pda_detector.channel_dict.values(),
            self.pda1_detector.channel_dict.values(),
        ):
            self.assertEqual(
                value_pda.get("Wavelength1"),
                value_pda1.get("Wavelength1"),
            )
            self.assertEqual(value_pda.get("Enable"), value_pda1.get("Enable"))

    def test_tuv_to_tuv(self):
        """Test transfer_wavelengths function for TUV to TUV
        Notes:
        - Modifies the tuv1 in place
        - transfer the wavelengths of the tuv detector to the tuv1 detector
        - the tuv1 detector should have the same wavelengths as the tuv detector
        """

        # Check input
        self.assertEqual(
            self.tuv_detector.channel_dict["Channel1"]["Wavelength"], "310.0"
        )
        self.assertEqual(
            self.tuv1_detector.channel_dict["Channel1"]["Wavelength"], "410.0"
        )

        # Run function
        transfer_wavelengths(self.tuv, self.tuv1)

        # Check output
        # iterate through the shortest channel_dict checking if the wavelengths
        for value_tuv, value_tuv1 in zip(
            self.tuv_detector.channel_dict.values(),
            self.tuv1_detector.channel_dict.values(),
        ):
            self.assertEqual(
                value_tuv.get("Wavelength"),
                value_tuv1.get("Wavelength"),
            )

    def test_pda_to_tuv(self):
        """Test transfer_wavelengths function for PDA to TUV
        Notes:
        - Modifies the tuv in place
        - transfer the wavelengths of the pda detector to the tuv detector
        - the tuv detector should have the same wavelengths as the pda detector
        """
        # Check input
        self.assertEqual(
            self.pda_detector.channel_dict["Channel1"]["Wavelength1"], "210.0"
        )
        self.assertEqual(
            self.tuv_detector.channel_dict["Channel1"]["Wavelength"], "310.0"
        )

        # Run function
        transfer_wavelengths(self.pda, self.tuv)

        # Check output
        # iterate through the shortest channel_dict checking if the wavelengths
        for value_pda, value_tuv in zip(
            self.pda_detector.channel_dict.values(),
            self.tuv_detector.channel_dict.values(),
        ):
            self.assertEqual(
                value_pda.get("Wavelength1"),
                value_tuv.get("Wavelength"),
            )

    def test_tuv_to_pda(self):
        """Test transfer_wavelengths function for TUV to PDA
        Notes:
        - Modifies the pda in place
        - transfer the wavelengths of the tuv detector to the pda detector
        - the pda detector should have the same wavelengths as the tuv detector
        """
        # Check input
        self.assertEqual(
            self.tuv_detector.channel_dict["Channel1"]["Wavelength"], "310.0"
        )
        self.assertEqual(
            self.pda_detector.channel_dict["Channel1"]["Wavelength1"], "210.0"
        )

        # Run function
        transfer_wavelengths(self.tuv, self.pda)

        # Check output
        # iterate through the shortest channel_dict checking if the wavelengths
        for value_tuv, value_pda in zip(
            self.tuv_detector.channel_dict.values(),
            self.pda_detector.channel_dict.values(),
        ):
            self.assertEqual(
                value_tuv.get("Wavelength"),
                value_pda.get("Wavelength1"),
            )
