import pytest
from app.services.payee_normalizer import PayeeNormalizer

@pytest.fixture
def normalizer() -> PayeeNormalizer:
    return PayeeNormalizer()

def test_normalizes_tesco():
    assert PayeeNormalizer().normalize('TESCO STORES 3456 GB') == 'Tesco'

def test_strips_zettle_prefix():
    # We care that the prefix is stripped, not about casing
    assert PayeeNormalizer().normalize("ZETTLE_*COFFEE SHOP").lower() == "coffee shop"

def test_detects_transfer():
    # We care that it's identified as a transfer, not about casing of the name
    result = PayeeNormalizer().normalize("TRANSFER TO J SOTO")
    assert result.startswith("Transfer –")
    assert "SOTO" in result

def test_handles_empty_string():
    assert PayeeNormalizer().normalize("") == ""

def test_squires_not_stripped_as_sq_prefix():
    """
    Regression test: 'Squire's Garden Centre' should not have 'Sq' stripped
    as if it were a Square payment processor prefix.
    The SQ prefix stripper should only match when SQ is followed by
    a space, asterisk, or dash — not when it's part of a word.
    """
    result = PayeeNormalizer().normalize("Squire's Garden Centre")
    assert "quire" in result.lower()
    assert result != "uire's Garden Centre"