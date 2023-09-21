import logging
import re

logger = logging.getLogger(__name__)


class InstrumentMethod:
    def __init__(self, method_definition):
        self.original_method = method_definition
        self._change_list = []

    def replace(self, original, new):
        self._change_list.append((original, new))

    @property
    def current_method(self):
        logger.debug("Applying changes to create current method")
        method = self.original_method.copy()
        try:
            xml: str = method["xml"]
        except KeyError:
            if len(self._change_list) > 0:
                raise ValueError(
                    "Cannot apply changes to method, no xml key in method definition."
                )
            else:
                # If there is no xml key, we can't do anything with the method. But if
                # there are no changes to apply, we can just return the original method.
                return method
        for original, new in self._change_list:
            logger.debug("Replacing %s with %s", original, new)
            num_replaced = xml.count(original)
            if num_replaced == 0:
                logger.warning(
                    f"Could not find {original} in {method}, no changes made to method."
                )
            else:
                xml = xml.replace(original, new)
                logger.debug(
                    "Replaced %s instances of %s with %s", num_replaced, original, new
                )
        method["xml"] = xml
        return method

    def __getitem__(self, key: str) -> str:
        try:
            xml = self.current_method["xml"]
        except KeyError:
            raise KeyError("No xml found in method definition")
        search_result = re.search(f"<{key}>(.*)</{key}>", xml)
        if not search_result:
            raise KeyError(f"Could not find key {key}")
        if f"<{key}>" in search_result.groups(1)[0]:
            # Python regex returns the maximum match, so if the key is found multiple
            # times, it will return everything between the first opening tag and the
            # last closing tag. This is not what we want, so we raise an error if this
            # happens.
            raise ValueError(f"Found more than one match for key {key}")
        return search_result.groups(1)[0]

    def __setitem__(self, key: str, value: str) -> NoReturn:
        current_value = self[key]
        self.replace(f"<{key}>{current_value}</{key}>", f"<{key}>{value}</{key}>")


class ColumnHandler(InstrumentMethod):
    temperature_key: str

    @property
    def column_temperature(self):
        return self[self.temperature_key]

    @column_temperature.setter
    def column_temperature(self, value: str) -> NoReturn:
        self[self.temperature_key] = value


class SampleManager(ColumnHandler):
    temperature_key = "ColumnTemperature"


def instrument_method_factory(method_definition: Mapping[str, str]) -> InstrumentMethod:
    """
    Factory function for creating an InstrumentMethod from a method definition. The
    method definition should contain at least a name key, which is used to determine
    which subclass of InstrumentMethod should be created. If the name key is not present
    or the name is not recognized, a generic InstrumentMethod will be created.
    """
    try:
        if method_definition["name"] in ["rAcquityFTN"]:
            logger.debug("Creating SampleManager")
            return SampleManager(method_definition)
        # Add more cases as they are coded
        else:
            logger.debug(
                "Unknown instrument method: %s, creating a generic InstrumentMethod",
                method_definition["name"],
            )  # The error is always caught, so we use the debug level here.
            raise ValueError(f"Unknown instrument method: {method_definition['name']}")
    except (KeyError, ValueError) as e:
        if isinstance(e, KeyError):
            # If the name key is not present, we don't know what to do with it, but we
            # can still create a generic InstrumentMethod and just return that.
            logger.debug("KeyError: %s, creating a generic InstrumentMethod", e)
        return InstrumentMethod(method_definition)
