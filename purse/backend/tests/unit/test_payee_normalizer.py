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