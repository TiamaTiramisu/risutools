"""Top-level package for risutools."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]

__author__ = """risu_uuid_generator"""
__email__ = "tiamatiramisu@proton.me"
__version__ = "0.0.1"

from .src.risutools.nodes import NODE_CLASS_MAPPINGS
from .src.risutools.nodes import NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"
