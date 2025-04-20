from inspect import cleandoc
from typing import  Literal
import os
import uuid
import hashlib

import numpy as np
from PIL import Image, ImageOps, ImageSequence, ImageFile, UnidentifiedImageError
import torch

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



def pillow(fn, arg):
    prev_value = None
    try:
        x = fn(arg)
    except (OSError, UnidentifiedImageError, ValueError): #PIL issues #4472 and #2445, also fixes ComfyUI issue #3416
        prev_value = ImageFile.LOAD_TRUNCATED_IMAGES
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        x = fn(arg)
    finally:
        if prev_value is not None:
            ImageFile.LOAD_TRUNCATED_IMAGES = prev_value
    return x

class LoadImageFromText:
    """
    Loads an image from a text

    This node loads a image string from a string input, a prefix, and a base directory.

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
            It is almost the same as LoadImage: https://github.com/comfyanonymous/ComfyUI/blob/fd274944418f1148b762a6e2d37efa820a569071/nodes.py#L1641
        """
        return {
            "required": {
                "name": ("STRING", {
                    "multiline": False,
                    "default": "image_name"
                }),
                "directory": ("STRING", {
                    "multiline": False,
                    "default": "absouute-path"
                })
            },
            "optional": {
                "prefix": ("STRING", {
                    "multiline": False,
                    "default": ""
                })
            }
        }

    RETURN_TYPES = ("IMAGE","MASK")
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "load_image_from_text"
    CATEGORY = "RisuTools/image"

    def load_image_from_text(self, name, directory, prefix = ""):
        if prefix == None: prefix = ""
        directory = directory.strip()
        image_path = os.path.join(directory, prefix + name)

        img = pillow(Image.open, image_path)

        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ['MPO']

        for i in ImageSequence.Iterator(img):
            i = pillow(ImageOps.exif_transpose, i)

            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]

            if image.size[0] != w or image.size[1] != h:
                continue

            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            elif i.mode == 'P' and 'transparency' in i.info:
                mask = np.array(i.convert('RGBA').getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)

    @classmethod
    def IS_CHANGED(cls, name, directory, prefix):
        if prefix == None: prefix = ""
        image_path = os.path.join(directory, prefix + name)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    #    @classmethod
    #    def VALIDATE_INPUTS(cls, name, directory, prefix = ""):
    #        if prefix == None: prefix = ""
    #        image_path = os.path.join(directory, prefix + name)
    #        if not os.path.exists(image_path):
    #            return f"invalid image file: {image_path}"
    #        return True

class LoadLastFileNamePrefix:
    """
    Loads the last filename containing the prefix in the directory

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
            It is almost the same as LoadImage: https://github.com/comfyanonymous/ComfyUI/blob/fd274944418f1148b762a6e2d37efa820a569071/nodes.py#L1641
        """
        return {
            "required": {
                "directory": ("STRING", {
                    "multiline": False,
                    "default": "absolute-path"
                })
            },
            "optional": {
                "prefix": ("STRING", {
                    "multiline": False,
                    "default": ""
                })
            }
        }

    RETURN_TYPES = ("STRING", )
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "load_filename"
    CATEGORY = "RisuTools/File"

    def load_filename(self, directory, prefix = ""):
        """
        Find the most recent file in the directory that starts with the given prefix.

        Parameters:
        -----------
        prefix : str
            The prefix to search for in filenames
        directory : str
            The directory to search in

        Returns:
        --------
        str
            The filename (without path) of the most recent file with the prefix
        """
        if prefix == None: prefix = ""
        directory = directory.strip()
        matching_files = []

        for filename in os.listdir(directory):
            if filename.startswith(prefix):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    matching_files.append((filename, os.path.getmtime(file_path)))

        if not matching_files:
            raise ValueError(f"No files found with prefix '{prefix}' in {directory}")

        # Sort by modification time (newest last)
        matching_files.sort(key=lambda x: x[1])

        # Return just the filename (without the path)
        return (matching_files[-1][0],)

    @classmethod
    def IS_CHANGED(cls, directory, prefix):
        m = uuid.uuid4().hex
        return m
    #   @classmethod
    #   def VALIDATE_INPUTS(cls, directory, prefix = ""):
    #       if prefix == None: prefix = ""
    #       if not os.path.exists(directory):
    #           return f"Directory does not exist: {directory}"

    #       if not os.path.isdir(directory):
    #           return f"Not a directory: {directory}"

    #       matching_files = [f for f in os.listdir(directory) if f.startswith(prefix) and os.path.isfile(os.path.join(directory, f))]

    #       if not matching_files:
    #           return f"There is no matching file with prefix '{prefix}' in {directory}"

    #       return True

class CheckFileNamePrefixExists:
    """
    Checks if any files with the given prefix exist in the directory

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
                "directory": ("STRING", {
                    "multiline": False,
                    "default": "absolute-path"
                })
            }, "optional": {
                "prefix": ("STRING", {
                    "multiline": False,
                    "default": ""
                })
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("exists",)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "check_filename_exists"
    CATEGORY = "RisuTools/File"

    def check_filename_exists(self, directory, prefix = ""):
        """
        Check if any files with the given prefix exist in the directory.

        Parameters:
        -----------
        prefix : str
            The prefix to search for in filenames
        directory : str
            The directory to search in

        Returns:
        --------
        bool
            True if at least one file with the prefix exists, False otherwise
        """
        if prefix == None: prefix = ""
        directory = directory.strip()
        if not os.path.exists(directory) or not os.path.isdir(directory):
            print(f"{not os.path.exists(directory)=} {not os.path.isdir(directory)}")
            return (False,)

        for filename in os.listdir(directory):
            if filename.startswith(prefix):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    print(f"Found file path: {file_path}")
                    return (True,)

        return (False,)

    @classmethod
    def IS_CHANGED(cls, directory, prefix):
        m = uuid.uuid4().hex
        return m
    #    @classmethod
    #    def VALIDATE_INPUTS(cls, directory, prefix = ""):
    #        if prefix == None: prefix = ""
    #        if not os.path.exists(directory):
    #            return f"Directory does not exist: {directory}"
    #
    #        if not os.path.isdir(directory):
    #            return f"Not a directory: {directory}"
    #
    #        return True






# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "UUIDGenerator": UUIDGenerator,
    "LoadImageFromText" : LoadImageFromText,
    "LoadLastFileNamePrefix" : LoadLastFileNamePrefix,
    "CheckFileNamePrefixExists" : CheckFileNamePrefixExists
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "UUIDGenerator": "UUID Generator",
    "LoadImageFromText" : "Load Image From Text",
    "LoadLastFileNamePrefix" : "Load Last File Name Prefix",
    "CheckFileNamePrefixExists" : "Check File Name Prefix Exists"
}

