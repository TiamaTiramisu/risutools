from .nodes import UUIDGenerator, LoadImageFromText
NODE_CLASS_MAPPINGS = {
    "UUIDGenerator": UUIDGenerator,
    "LoadImageFromText" : LoadImageFromText }
__all__ = ["NODE_CLASS_MAPPINGS"]
