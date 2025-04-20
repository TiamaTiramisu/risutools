from inspect import cleandoc
from typing import  Literal
import uuid

UUIDVersions = Literal["v1", "v3", "v4", "v5"]
class UUIDGenerator:
    """
    A UUID generator node

    This node generates a UUID string based on a string input. It can generate different
    types of UUIDs and optionally use the input string as a namespace.

    Class methods
    -------------
    INPUT_TYPES (dict):
        Tell the main program input parameters of nodes.

    Attributes
    ----------
    RETURN_TYPES (`tuple`):
        The type of each element in the output tuple.
    RETURN_NAMES (`tuple`):
        The name of each output in the output tuple.
    FUNCTION (`str`):
        The name of the entry-point method.
    CATEGORY (`str`):
        The category the node should appear in the UI.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """
            Return a dictionary which contains config for all input fields.
        """
        return {
            "required": {
                "input_string": ("STRING", {
                    "multiline": False,
                    "default": "seed string"
                }),
                "uuid_version": (["v1", "v3", "v4", "v5"], { "default" : "v5" })
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("uuid",)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "generate_uuid"

    CATEGORY = "RisuTools/String"

    def generate_uuid(self, input_string,  uuid_version : UUIDVersions = "v5"):
        namespace = uuid.UUID('0413fcc2-9f97-5739-82fd-523d122514b7')
        # Generate UUID based on version
        if uuid_version == "v1":
            # Version 1: Time-based
            result = str(uuid.uuid1())
        elif uuid_version == "v3":
            # Version 3: MD5 hash of namespace + name
            result = str(uuid.uuid3(namespace, input_string))
        elif uuid_version == "v4":
            # Version 4: Random
            result = str(uuid.uuid4())
        elif uuid_version == "v5":
            # Version 5: SHA-1 hash of namespace + name
            result = str(uuid.uuid5(namespace, input_string))

        return (result,)


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "UUIDGenerator": UUIDGenerator
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "UUIDGenerator": "UUID Generator"
}

