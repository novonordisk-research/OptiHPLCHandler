from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from .data_types import HplcResult, HPLCSetup, Sample
from .empower_api_core import EmpowerConnection

Result = TypeVar("Result")

Setup = TypeVar("Setup")


class InstrumentHandler(ABC, Generic[Result, Setup]):
    def __init__(self, run_automatically: bool):
        self.run_automatically = run_automatically

    @property
    @abstractmethod
    def Status(self) -> List[Result]:
        pass

    @abstractmethod
    def Post(experiment: Any) -> Result:
        """
        Post the experiment to the instrument.

        If the InstrumentHandler is set to run automatically, this will also run the experiment.
        """
        pass

    @abstractmethod
    def GetSetup() -> List[Setup]:
        pass


class EmpowerHandler(InstrumentHandler):
    def __init__(
        self,
        project: str,
        address: str,
        username: Optional[str] = None,
        service: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.connection = EmpowerConnection(
            project=project, address=address, username=username, service=service
        )

    @property
    def project(self) -> str:
        return self.connection.project

    @property
    def address(self) -> str:
        return self.connection.address

    @property
    def username(self) -> str:
        return self.connection.username

    def Status(self) -> List[HplcResult]:
        """Get the status of the HPLC."""
        raise NotImplementedError

    def Post(
        self,
        sample_set_name: str,
        sample_list: List[Sample],
        plate_list: List[Any],
        audit_trail_message: str,
        hplc: Optional[str] = None,
    ) -> List[HplcResult]:
        """
        Post the experiment to the HPLC. Also runs them if the InstrumentHandler is set to run automatically.


        :param sample_set_name: Name of the sample set method. This will be the name of the sample set in Empower.

        :param sample_list: List of samples to run. Each sample is a dictionary with the following keys:
            - Method: Name of the method to use for the sample
            - SamplePos: Position of the sample in the autosampler, including plate and position on the plate
            - SampleName: Name of the sample
            - InjectionVolume: Volume of the sample to inject in micro liters
            - OtherFields: List of other fields to add to the sample. Each field is a dictionary with the
                following keys:
                - name: Name of the field
                - value: Value of the field. Can be a string, number, or dictionary with the following keys:
                    - member: Name of the member to use for the field
                    - value: Value of the member
            For all fields, the datatype will be autodetermined according the the type of the value. For Boolean
            values, this will errouneously be set to string. Instead, use `"value": {"member": “No”}` or
            `"value": {"member": “Yes”}`

        :param plate_list: List of plates to use. Each plate is a dictionary with the following keys:
            - plateTypeName: Name of the plate type
            - position: Position of the plate in the autosampler. This is what you reference in
                the sample value "SamplePos"

        :param audit_trail_message: Message to add to the audit trail of the sample set method

        :param hplc: Name of the HPLC to run the samples on. If not specified, the samples can not be run.
            If the InstrumentHandler is set to be run automatically, this will raise an error.

        :return:

            - hplc_result_list: List of results of the samples. Each result is a dictionary with the following keys:
                - StartTime: The (possibly expected) time of the injection
                - EndTime: The (possibly expected) end time of the analysis
                - PerformedExperiment: The experiment that was run
                - Data: A reference to where the raw data of the experiment is stored

        """
        sampleset_object = {"plates": plate_list}
        empower_sample_list = []
        for num, sample in enumerate(sample_list):
            field_list = [
                {"name": "Function", "value": {"member": "Inject Samples"}},
                {"name": "Processing", "value": {"member": "Normal"}},
                {"name": "MethodSetOrReportMethod", "value": sample["Method"]},
                {"name": "Vial", "value": sample["SamplePos"]},
                {"name": "SampleName", "value": sample["SampleName"]},
                {"name": "InjVol", "value": sample["InjectionVolume"]},
            ]
            other_fields = sample.get("OtherFields", [])
            # Getting the other fields to add, or an empty list if no other fields are given.
            for field in other_fields:
                field_list.append(field)
            for field in field_list:
                self.set_data_type(field)
            empower_sample_list.append(
                {"components": [], "id": num, "fields": field_list}
            )
        sampleset_object["sampleSetLines"] = empower_sample_list
        endpoint = f"project/methods/sample-set-method?name={sample_set_name}"
        if audit_trail_message:
            endpoint += f"&AtComment={audit_trail_message}"
        response = self.connection.post(endpoint=endpoint, body=sampleset_object)
        if self.run_automatically:
            if hplc is None:
                raise ValueError("No HPLC specified.")
            raise NotImplementedError  # Run the sample set, and find the expected start and end times
        return response.json()["results"]  # Wrong return type

    def AddMethod(
        self,
        template_method: str,
        new_method: str,
        changes: Dict[str, Any],
        audit_trail_message: str,
    ) -> None:
        """Add a new method based on the template method."""
        raise NotImplementedError

    def GetMethodList(self) -> List[str]:
        """Get the list of methods"""
        response = self.connection.get(
            endpoint="project/methods?methodTypes=MethodSetMethod"
        )
        method_name_dict_list = [
            [name_dict for name_dict in method["fields"] if name_dict["name"] == "Name"]
            for method in response.json()["results"]
        ]
        if any([len(name_dict) > 1 for name_dict in method_name_dict_list]):
            raise ValueError("Multiple names found for a method.")
        if any([len(name_dict) == 0 for name_dict in method_name_dict_list]):
            raise ValueError("No name found for a method.")
        method_name_list = [
            name_dict[0]["value"] for name_dict in method_name_dict_list
        ]
        return method_name_list

    def GetSetup(self) -> List[HPLCSetup]:
        """Get the list of HPLC setups"""
        # This is almost certainly an incredibly naive use of the API. Fill out with correct details when available.
        raise NotImplementedError

    def set_data_type(self, field: Dict[str, Any]) -> Dict[str, Any]:
        data_type_dict = {
            str: "String",
            int: "Double",
            float: "Double",
            dict: "Enumerator",
        }
        data_type = type(field["value"])
        field["dataType"] = data_type_dict[data_type]
