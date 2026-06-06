# path: tests/test_bitnet.py

"""
BitNet 1.58 / 3.0 compatibility and translation tests
"""

import pytest

from src.bitnet_runner import BitNetRunner


def test_runner_1_58():
    r = BitNetRunner(bitnet_version="1.58")
    assert r.bitnet_version == "1.58"


def test_runner_3_0():
    r = BitNetRunner(bitnet_version="3.0")
    assert r.bitnet_version == "3.0"


def test_translation():
    r = BitNetRunner()
    code = "print('hello')"
    translated = r.translate_to_bitnet(code)
    assert "BitNet" in translated
