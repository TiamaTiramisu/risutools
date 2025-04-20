#!/usr/bin/env python

"""Tests for `risutools` package."""

import pytest
import uuid
from src.risutools.nodes import UUIDGenerator

@pytest.fixture
def uuid_generator_node():
    """Fixture to create a UUIDGenerator node instance."""
    return UUIDGenerator()

def test_uuid_generator_initialization(uuid_generator_node):
    """Test that the node can be instantiated."""
    assert isinstance(uuid_generator_node, UUIDGenerator)

def test_return_types():
    """Test the node's metadata."""
    assert UUIDGenerator.RETURN_TYPES == ("STRING",)
    assert UUIDGenerator.RETURN_NAMES == ("uuid",)
    assert UUIDGenerator.FUNCTION == "generate_uuid"
    assert UUIDGenerator.CATEGORY == "RisuTools/String"

def test_uuid_generation_v5():
    """Test UUID v5 generation."""
    node = UUIDGenerator()
    test_string = "test string"
    result, = node.generate_uuid(test_string, "v5")

    # Verify it's a valid UUID string
    assert uuid.UUID(result)

    # Verify deterministic behavior - same input should produce same UUID
    result2, = node.generate_uuid(test_string, "v5")
    assert result == result2

    # Different input should produce different UUID
    result3, = node.generate_uuid("different string", "v5")
    assert result != result3

def test_uuid_generation_v4():
    """Test UUID v4 generation (random)."""
    node = UUIDGenerator()
    result, = node.generate_uuid("any string", "v4")

    # Verify it's a valid UUID string
    assert uuid.UUID(result)

    # v4 is random, so multiple calls should produce different results
    # Note: There's a tiny probability this could fail by random chance
    result2, = node.generate_uuid("any string", "v4")
    assert result != result2

def test_uuid_generation_v3():
    """Test UUID v3 generation."""
    node = UUIDGenerator()
    test_string = "test string"
    result, = node.generate_uuid(test_string, "v3")

    # Verify it's a valid UUID string
    assert uuid.UUID(result)

    # Verify deterministic behavior - same input should produce same UUID
    result2, = node.generate_uuid(test_string, "v3")
    assert result == result2

def test_uuid_generation_v1():
    """Test UUID v1 generation (time-based)."""
    node = UUIDGenerator()
    result, = node.generate_uuid("any string", "v1")

    # Verify it's a valid UUID string
    assert uuid.UUID(result)
