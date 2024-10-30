import unittest
from types import SimpleNamespace
from typing import Union

from OptiHPLCHandler.applications.method_converter.method_converter import (
    change_wavelengths,
    transfer_gradient_table,
    transfer_wavelengths,
)
from OptiHPLCHandler.empower_module_method import (
    ColumnManagerMethod,
    EmpowerModuleMethod,
    SampleManagerMethod,
    SolventManagerMethod,
)


class BSMMethod(SimpleNamespace):
    """
    Mock class for BSMMethod
    """

    def __init__(self, solvent_lines: list = ["A1", "B1"]):
        self.solvent_lines = solvent_lines


class QSMMethod(SimpleNamespace):
    """
    Mock class for QSMMethod
    """

    def __init__(self, solvent_lines: list = ["A", "B", "C", "D1"]):
        self.solvent_lines = solvent_lines


class PDAMethod(SimpleNamespace):
    """
    Mock class for PDAMethod
    """

    def __init__(self, channel_dict, lamp_enabled):
        self.channel_dict = channel_dict
        self.lamp_enabled = lamp_enabled


class TUVMethod(SimpleNamespace):
    """
    Mock class for TUVMethod
    """

    def __init__(self, channel_dict, lamp_enabled):
        self.channel_dict = channel_dict
        self.lamp_enabled = lamp_enabled


class EmpowerInstrumentMethodMock(SimpleNamespace):
    """
    Mock class for EmpowerInstrumentMethod
    """

    def __init__(
        self,
        gradient_table,
        method_name,
        solvent_handler_method,
        detector_method_list,
    ):
        self.gradient_table: list[dict] = gradient_table
        self.method_name: str = method_name
        self.solvent_handler_method: Union[BSMMethod, QSMMethod] = (
            solvent_handler_method
        )
        self.detector_method_list: list[
            Union[
                EmpowerModuleMethod,
                SampleManagerMethod,
                ColumnManagerMethod,
                SolventManagerMethod,
                PDAMethod,
                TUVMethod,
            ]
        ] = detector_method_list

    def copy(self):
        # make new instance of the class
        new_name = self.method_name + "_copy"
        return EmpowerInstrumentMethodMock(
            self.gradient_table,
            new_name,
            self.solvent_handler_method,
            self.detector_method_list,
        )

    def __str__(self):
        return f"Method: {self.method_name}, Gradient Table: {self.gradient_table}, Solvent Handler: {self.solvent_handler_method}, Detector Method: {self.detector_method_list}"  # noqa E501


class TestTransferGradient(unittest.TestCase):
    def setUp(self):
        self.bsm_mock_initial = EmpowerInstrumentMethodMock(
            [
                {
                    "Time": "Initial",
                    "Flow": 0.3,
                    "CompositionA": 90.0,
                    "CompositionB": 10.0,
                    "Curve": "Initial",
                },
                {
                    "Time": 5.0,
                    "Flow": 0.3,
                    "CompositionA": 10.0,
                    "CompositionB": 90.0,
                    "Curve": 6,
                },
                {
                    "Time": 7.0,
                    "Flow": 0.3,
                    "CompositionA": 10.0,
                    "CompositionB": 90.0,
                    "Curve": 6,
                },
                {
                    "Time": 7.1,
                    "Flow": 0.3,
                    "CompositionA": 90.0,
                    "CompositionB": 10.0,
                    "Curve": 6,
                },
                {
                    "Time": 10.0,
                    "Flow": 0.3,
                    "CompositionA": 90.0,
                    "CompositionB": 10.0,
                    "Curve": 6,
                },
            ],
            "BSMMock",
            BSMMethod(),
            [],
        )

        self.bsm_mock_initial_2 = EmpowerInstrumentMethodMock(
            [
                {
                    "Time": "Initial",
                    "Flow": 0.3,
                    "CompositionA": 70.0,
                    "CompositionB": 30.0,
                    "Curve": "Initial",
                },
                {
                    "Time": 5.0,
                    "Flow": 0.3,
                    "CompositionA": 10.0,
                    "CompositionB": 90.0,
                    "Curve": 6,
                },
                {
                    "Time": 7.0,
                    "Flow": 0.3,
                    "CompositionA": 10.0,
                    "CompositionB": 90.0,
                    "Curve": 6,
                },
                {
                    "Time": 7.1,
                    "Flow": 0.3,
                    "CompositionA": 70.0,
                    "CompositionB": 30.0,
                    "Curve": 6,
                },
                {
                    "Time": 10.0,
                    "Flow": 0.3,
                    "CompositionA": 70.0,
                    "CompositionB": 30.0,
                    "Curve": 6,
                },
            ],
            "BSMMock",
            BSMMethod(),
            [],
        )

        self.qsm_mock_initial = EmpowerInstrumentMethodMock(
            [
                {
                    "Time": "Initial",
                    "Flow": 0.3,
                    "CompositionA": 80.0,
                    "CompositionB": 20.0,
                    "CompositionC": 0.0,
                    "CompositionD": 0.0,
                    "Curve": "Initial",
                },
                {
                    "Time": 5.0,
                    "Flow": 0.3,
                    "CompositionA": 10.0,
                    "CompositionB": 90.0,
                    "CompositionC": 0.0,
                    "CompositionD": 0.0,
                    "Curve": 6,
                },
                {
                    "Time": 7.0,
                    "Flow": 0.3,
                    "CompositionA": 10.0,
                    "CompositionB": 90.0,
                    "CompositionC": 0.0,
                    "CompositionD": 0.0,
                    "Curve": 6,
                },
                {
                    "Time": 7.1,
                    "Flow": 0.3,
                    "CompositionA": 80.0,
                    "CompositionB": 20.0,
                    "CompositionC": 0.0,
                    "CompositionD": 0.0,
                    "Curve": 6,
                },
                {
                    "Time": 10.0,
                    "Flow": 0.3,
                    "CompositionA": 80.0,
                    "CompositionB": 20.0,
                    "CompositionC": 0.0,
                    "CompositionD": 0.0,
                    "Curve": 6,
                },
            ],
            "QSMMock",
            QSMMethod(),
            [],
        )

        self.qsm_mock_initial_2 = EmpowerInstrumentMethodMock(
            [
                {
                    "Time": "Initial",
                    "Flow": 0.3,
                    "CompositionC": 70.0,
                    "CompositionD": 30.0,
                    "CompositionA": 0.0,
                    "CompositionB": 0.0,
                    "Curve": "Initial",
                },
                {
                    "Time": 5.0,
                    "Flow": 0.3,
                    "CompositionC": 10.0,
                    "CompositionD": 90.0,
                    "CompositionA": 0.0,
                    "CompositionB": 0.0,
                    "Curve": 6,
                },
                {
                    "Time": 7.0,
                    "Flow": 0.3,
                    "CompositionC": 10.0,
                    "CompositionD": 90.0,
                    "CompositionA": 0.0,
                    "CompositionB": 0.0,
                    "Curve": 6,
                },
                {
                    "Time": 7.1,
                    "Flow": 0.3,
                    "CompositionC": 70.0,
                    "CompositionD": 30.0,
                    "CompositionA": 0.0,
                    "CompositionB": 0.0,
                    "Curve": 6,
                },
                {
                    "Time": 10.0,
                    "Flow": 0.3,
                    "CompositionC": 70.0,
                    "CompositionD": 30.0,
                    "CompositionA": 0.0,
                    "CompositionB": 0.0,
                    "Curve": 6,
                },
            ],
            "QSMMock",
            QSMMethod(),
            [],
        )

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
        bsm_mock = self.bsm_mock_initial.copy()
        self.assertEqual(bsm_mock.gradient_table[0]["CompositionA"], 90.0)
        qsm_mock = self.qsm_mock_initial.copy()
        self.assertEqual(qsm_mock.gradient_table[0]["CompositionA"], 80.0)

        # Run function
        transfer_gradient_table(bsm_mock, qsm_mock)

        # Check output
        self.assertEqual(qsm_mock.gradient_table[0]["CompositionA"], 90.0)
        self.assertTrue("CompositionB" in qsm_mock.gradient_table[0])
        self.assertTrue("CompositionC" in qsm_mock.gradient_table[0])
        self.assertTrue("CompositionD" in qsm_mock.gradient_table[0])

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
        bsm_mock = self.bsm_mock_initial.copy()
        self.assertEqual(bsm_mock.gradient_table[0]["CompositionA"], 90.0)
        qsm_mock = self.qsm_mock_initial.copy()
        self.assertEqual(qsm_mock.gradient_table[0]["CompositionA"], 80.0)

        # Run function
        transfer_gradient_table(qsm_mock, bsm_mock)

        # Check output
        self.assertEqual(bsm_mock.gradient_table[0]["CompositionA"], 80.0)
        self.assertTrue("CompositionB" in qsm_mock.gradient_table[0])
        self.assertFalse("CompositionC" in bsm_mock.gradient_table[0])
        self.assertFalse("CompositionD" in bsm_mock.gradient_table[0])

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
        bsm_mock = self.bsm_mock_initial.copy()
        self.assertEqual(bsm_mock.gradient_table[0]["CompositionA"], 90.0)
        bsm_mock_2 = self.bsm_mock_initial_2.copy()
        self.assertEqual(bsm_mock_2.gradient_table[0]["CompositionA"], 70.0)

        # Run function
        transfer_gradient_table(bsm_mock, bsm_mock_2)

        # Check output
        self.assertEqual(bsm_mock_2.gradient_table[0]["CompositionA"], 90.0)
        self.assertTrue("CompositionB" in bsm_mock_2.gradient_table[0])
        self.assertFalse("CompositionC" in bsm_mock_2.gradient_table[0])
        self.assertFalse("CompositionD" in bsm_mock_2.gradient_table[0])

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
        qsm_mock = self.qsm_mock_initial.copy()
        self.assertEqual(qsm_mock.gradient_table[0]["CompositionA"], 80.0)
        qsm_mock_2 = self.qsm_mock_initial_2.copy()
        self.assertEqual(qsm_mock_2.gradient_table[0]["CompositionC"], 70.0)

        # Run function
        transfer_gradient_table(qsm_mock, qsm_mock_2)

        # Check output
        self.assertEqual(qsm_mock_2.gradient_table[0]["CompositionC"], 80.0)
        self.assertTrue("CompositionA" in qsm_mock_2.gradient_table[0])
        self.assertTrue("CompositionB" in qsm_mock_2.gradient_table[0])
        self.assertTrue("CompositionD" in qsm_mock_2.gradient_table[0])

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
        bsm_mock = self.bsm_mock_initial.copy()
        self.assertEqual(bsm_mock.gradient_table[0]["CompositionA"], 90.0)
        qsm_mock = self.qsm_mock_initial_2.copy()
        self.assertEqual(qsm_mock.gradient_table[0]["CompositionC"], 70.0)

        # Run function
        transfer_gradient_table(qsm_mock, bsm_mock)

        # Check output
        self.assertEqual(bsm_mock.gradient_table[0]["CompositionA"], 70.0)
        self.assertEqual(bsm_mock.gradient_table[0]["CompositionB"], 30.0)
        self.assertFalse("CompositionC" in bsm_mock.gradient_table[0])
        self.assertFalse("CompositionD" in bsm_mock.gradient_table[0])


class TestChangeWavelengths(unittest.TestCase):
    def setUp(self):
        self.pda = {
            "Channel1": {"Wavelength1": 210.0, "Enabled": True},
            "Channel2": {"Wavelength1": 220.0, "Enabled": True},
            "Channel3": {"Wavelength1": 230.0, "Enabled": False},
            "Channel4": {"Wavelength1": 240.0, "Enabled": False},
            "Channel5": {"Wavelength1": 250.0, "Enabled": False},
            "Channel6": {"Wavelength1": 260.0, "Enabled": False},
            "Channel7": {"Wavelength1": 270.0, "Enabled": False},
            "Channel8": {"Wavelength1": 280.0, "Enabled": False},
        }
        self.pda1 = {
            "Channel1": {"Wavelength1": 110.0, "Enabled": True},
            "Channel2": {"Wavelength1": 120.0, "Enabled": False},
            "Channel3": {"Wavelength1": 130.0, "Enabled": False},
            "Channel4": {"Wavelength1": 140.0, "Enabled": False},
            "Channel5": {"Wavelength1": 150.0, "Enabled": False},
            "Channel6": {"Wavelength1": 160.0, "Enabled": False},
            "Channel7": {"Wavelength1": 170.0, "Enabled": False},
            "Channel8": {"Wavelength1": 180.0, "Enabled": False},
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
        pda = self.pda.copy()
        pda1 = self.pda1.copy()

        # Check input
        self.assertEqual(pda["Channel1"]["Wavelength1"], 210.0)
        self.assertEqual(pda1["Channel1"]["Wavelength1"], 110.0)
        self.assertTrue(pda["Channel1"]["Enabled"])
        self.assertTrue(pda1["Channel1"]["Enabled"])

        # Run function
        change_wavelengths(pda, pda1)

        # Check output
        for value_pda, value_pda1 in zip(pda.values(), pda1.values()):
            self.assertEqual(
                value_pda.get("Wavelength1", value_pda.get("Wavelength1")),
                value_pda1.get("Wavelength1"),
            )
            self.assertEqual(value_pda.get("Enabled"), value_pda1.get("Enabled"))

    def test_pda_to_tuv(self):
        """Test change_wavelengths function for PDA to TUV
        Notes:
        - Modifies the tuv in place
        - change the wavelengths of the pda dictionary to match the tuv dictionary
        - the tuv should have the same wavelengths as the pda dictionary
        """
        pda = self.pda.copy()
        tuv = self.tuv.copy()

        # Check input
        self.assertEqual(pda["Channel1"]["Wavelength1"], 210.0)
        self.assertEqual(tuv["Channel1"]["Wavelength"], 310.0)

        # Run function
        change_wavelengths(pda, tuv)

        # Check output
        for value_pda, value_tuv in zip(pda.values(), tuv.values()):
            self.assertEqual(
                value_pda.get("Wavelength1", value_pda.get("Wavelength1")),
                value_tuv.get("Wavelength"),
            )

    def test_tuv_to_pda(self):
        """Test change_wavelengths function for TUV to PDA
        Notes:
        - Modifies the pda in place
        - change the wavelengths of the tuv dictionary to match the pda dictionary
        - the pda should have the same wavelengths as the tuv dictionary
        """
        tuv = self.tuv.copy()
        pda = self.pda.copy()

        # Check input
        self.assertEqual(tuv["Channel1"]["Wavelength"], 310.0)
        self.assertEqual(pda["Channel1"]["Wavelength1"], 210.0)

        # Run function
        change_wavelengths(tuv, pda)

        # Check output
        for value_tuv, value_pda in zip(tuv.values(), pda.values()):
            self.assertEqual(
                value_tuv.get("Wavelength", value_tuv.get("Wavelength")),
                value_pda.get("Wavelength1"),
            )

    def test_tuv_to_tuv(self):
        """Test change_wavelengths function for TUV to TUV
        Notes:
        - Modifies the tuv1 in place
        - change the wavelengths of the tuv dictionary to match the tuv1 dictionary
        - the tuv1 should have the same wavelengths as the tuv dictionary
        """
        tuv = self.tuv.copy()
        tuv1 = self.tuv1.copy()

        # Check input
        self.assertEqual(tuv["Channel1"]["Wavelength"], 310.0)
        self.assertEqual(tuv1["Channel1"]["Wavelength"], 410.0)

        # Run function
        change_wavelengths(tuv, tuv1)

        # Check output
        for value_tuv, value_tuv1 in zip(tuv.values(), tuv1.values()):
            self.assertEqual(
                value_tuv.get("Wavelength", value_tuv.get("Wavelength")),
                value_tuv1.get("Wavelength"),
            )


class TestTransferWavelengths(unittest.TestCase):
    def setUp(self):
        self.channel_dict_pda = {
            "Channel1": {"Wavelength1": 210.0, "Enabled": True},
            "Channel2": {"Wavelength1": 220.0, "Enabled": True},
            "Channel3": {"Wavelength1": 230.0, "Enabled": False},
            "Channel4": {"Wavelength1": 240.0, "Enabled": False},
            "Channel5": {"Wavelength1": 250.0, "Enabled": False},
            "Channel6": {"Wavelength1": 260.0, "Enabled": False},
            "Channel7": {"Wavelength1": 270.0, "Enabled": False},
            "Channel8": {"Wavelength1": 280.0, "Enabled": False},
        }

        self.channel_dict_pda1 = {
            "Channel1": {"Wavelength1": 310.0, "Enabled": True},
            "Channel2": {"Wavelength1": 320.0, "Enabled": True},
            "Channel3": {"Wavelength1": 330.0, "Enabled": False},
            "Channel4": {"Wavelength1": 340.0, "Enabled": False},
            "Channel5": {"Wavelength1": 350.0, "Enabled": False},
            "Channel6": {"Wavelength1": 360.0, "Enabled": False},
            "Channel7": {"Wavelength1": 370.0, "Enabled": False},
            "Channel8": {"Wavelength1": 380.0, "Enabled": False},
        }

        self.channel_dict_tuv = {
            "Channel1": {"Wavelength": 310.0},
            "Channel2": {"Wavelength": 320.0},
        }
        self.channel_dict_tuv1 = {
            "Channel1": {"Wavelength": 410.0},
            "Channel2": {"Wavelength": 420.0},
        }

        self.tuv_method = EmpowerInstrumentMethodMock(
            [{}], "tuv_method", BSMMethod(), [TUVMethod(self.channel_dict_tuv, True)]
        )

        self.tuv_method1 = EmpowerInstrumentMethodMock(
            [{}], "tuv_method", BSMMethod(), [TUVMethod(self.channel_dict_tuv1, True)]
        )

        self.pda_method = EmpowerInstrumentMethodMock(
            [{}], "pda_method", BSMMethod(), [PDAMethod(self.channel_dict_pda, True)]
        )

        self.pda_method1 = EmpowerInstrumentMethodMock(
            [{}], "pda_method", BSMMethod(), [PDAMethod(self.channel_dict_pda1, True)]
        )

    def test_pda_to_tuv(self):
        """Test transfer_wavelengths function for PDA to TUV
        Notes:
        - Modifies the tuv_method in place
        - transfer the wavelengths from the pda_method to the tuv_method
        - the tuv_method should have the same wavelengths as the pda_method
        """
        # Check input
        pda_method = self.pda_method.copy()
        tuv_method = self.tuv_method.copy()
        self.assertEqual(
            tuv_method.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength": 310.0},
        )
        self.assertEqual(
            pda_method.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength1": 210.0, "Enabled": True},
        )

        # Run function
        transfer_wavelengths(pda_method, tuv_method)

        # Check output
        self.assertEqual(
            tuv_method.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength": 210.0},
        )

    def test_tuv_to_pda(self):
        """Test transfer_wavelengths function for PDA to TUV
        Notes:
        - Modifies the tuv_method in place
        - transfer the wavelengths from the pda_method to the tuv_method
        - the tuv_method should have the same wavelengths as the pda_method
        """
        # Check input
        pda_method = self.pda_method.copy()
        tuv_method = self.tuv_method.copy()
        self.assertEqual(
            tuv_method.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength": 310.0},
        )
        self.assertEqual(
            pda_method.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength1": 210.0, "Enabled": True},
        )

        # Run function
        transfer_wavelengths(tuv_method, pda_method)

        # Check output
        self.assertEqual(
            pda_method.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength1": 310.0, "Enabled": True},
        )

    def test_pda_to_pda(self):
        """Test transfer_wavelengths function for PDA to PDA
        Notes:
        - Modifies the pda_method in place
        - transfer the wavelengths from the pda_method to the pda_method1
        - the pda_method1 should have the same wavelengths as the pda_method
        """
        # Check input
        pda_method = self.pda_method.copy()
        pda_method1 = self.pda_method1.copy()
        self.assertEqual(
            pda_method1.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength1": 310.0, "Enabled": True},
        )
        self.assertEqual(
            pda_method.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength1": 210.0, "Enabled": True},
        )

        # Run function
        transfer_wavelengths(pda_method, pda_method1)

        # Check output
        self.assertEqual(
            pda_method1.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength1": 210.0, "Enabled": True},
        )

    def test_tuv_to_tuv(self):
        """Test transfer_wavelengths function for TUV to TUV
        Notes:
        - Modifies the tuv_method in place
        - transfer the wavelengths from the tuv_method to the tuv_method1
        - the tuv_method1 should have the same wavelengths as the tuv_method
        """
        # Check input
        tuv_method = self.tuv_method.copy()
        tuv_method1 = self.tuv_method1.copy()
        self.assertEqual(
            tuv_method1.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength": 410.0},
        )
        self.assertEqual(
            tuv_method.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength": 310.0},
        )

        # Run function
        transfer_wavelengths(tuv_method, tuv_method1)

        # Check output
        self.assertEqual(
            tuv_method1.detector_method_list[0].channel_dict["Channel1"],
            {"Wavelength": 310.0},
        )


if __name__ == "__main__":
    unittest.main()
