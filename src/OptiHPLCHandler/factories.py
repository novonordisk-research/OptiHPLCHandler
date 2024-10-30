import logging
from typing import Mapping
from xml.etree import ElementTree as ET

from .empower_detector_module_method import FLRMethod, PDAMethod, TUVMethod
from .empower_module_method import (
    BSMMethod,
    ColumnManagerMethod,
    EmpowerModuleMethod,
    QSMMethod,
    SampleManagerMethod,
)

logger = logging.getLogger(__name__)


def module_method_factory(  # noqa: C901 This method is allowed to be "complex"
    method_definition: Mapping[str, str]
) -> EmpowerModuleMethod:
    """
    Factory function for creating an EmpowerModuleMethod from a method definition. The
    method definition should contain at least a name key, which is used to determine
    which subclass should be created. If the name key is not present or the name is not
    recognized, a generic EmpowerModuleMethod will be created.
    """
    try:
        try:
            module_type = method_definition["name"]
        except KeyError:
            tree = ET.fromstring(method_definition["nativeXml"])
            module_type = tree.tag
        if "FTN" in module_type or "AcquitySM" in module_type:
            logger.debug("Creating SampleManagerMethod")
            return SampleManagerMethod(method_definition)
        if "AcquityCM" in module_type or "ACQ-CM" in module_type:
            logger.debug("Creating ColumnManagerMethod")
            return ColumnManagerMethod(method_definition)
        if "AcquityBSM" in module_type or "ACQ-BSM" in module_type:
            logger.debug("Creating BSMMethod")
            return BSMMethod(method_definition)
        if "AcquityQSM" in module_type or "ACQ-QSM" in module_type:
            logger.debug("Creating QSMMethod")
            return QSMMethod(method_definition)
        if "AcquityFLR" in module_type or "ACQ-FLR" in module_type:
            logger.debug("Creating FLRMethod")
            return FLRMethod(method_definition)
        if "AcquityTUV" in module_type or "ACQ-TUV" in module_type:
            logger.debug("Creating TUVMethod")
            return TUVMethod(method_definition)
        if "AcquityPDA" in module_type or "ACQ-PDA" in module_type:
            logger.debug("Creating PDAMethod")
            return PDAMethod(method_definition)
        # Add more cases as they are coded
        else:
            logger.debug(
                "Unknown module method: %s, creating a generic EmpowerModuleMethod",
                module_type,
            )  # The error is always caught, so we use the debug level here.
            raise ValueError(f"Unknown module method: {method_definition['name']}")
    except (KeyError, ValueError) as e:
        if isinstance(e, KeyError):
            # If the name key is not present, we don't know what to do with it, but we
            # can still create a generic EmpowerModuleMethod and just return that.
            logger.debug("KeyError: %s, creating a generic EmpowerModuleMethod", e)
        return EmpowerModuleMethod(method_definition)
