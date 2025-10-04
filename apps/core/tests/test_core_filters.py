import pytest

from apps.core.templatetags.core_filters import to_roman


def test_to_roman_converts_1_to_I():
    assert to_roman(1) == "I"


def test_to_roman_converts_5_to_V():
    assert to_roman(5) == "V"


def test_to_roman_converts_10_to_X():
    assert to_roman(10) == "X"


def test_to_roman_converts_4_to_IV():
    assert to_roman(4) == "IV"


def test_to_roman_converts_9_to_IX():
    assert to_roman(9) == "IX"


def test_to_roman_converts_various_numbers():
    assert to_roman(2) == "II"
    assert to_roman(3) == "III"
    assert to_roman(6) == "VI"
    assert to_roman(7) == "VII"
    assert to_roman(8) == "VIII"


def test_to_roman_returns_empty_string_for_zero():
    assert to_roman(0) == ""


def test_to_roman_returns_empty_string_for_negative():
    assert to_roman(-1) == ""


def test_to_roman_returns_empty_string_for_non_integer():
    assert to_roman("not a number") == ""
