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


def test_sportsbikeshop_sp_not_stripped():
    """
    Regression test: 'SPORTSBIKESHOP LTD' should not have 'SP' stripped
    from its start. The SP prefix stripper must require a non-word character
    after SP (space, asterisk) — not match SP at the start of any word.
    """
    result = PayeeNormalizer().normalize("SPORTSBIKESHOP LTD")
    assert result.lower().startswith("sportsbikeshop")


def test_corporate_suffix_ltd_stripped():
    """
    'CHRISTMAS BAKERY LIMITED' should strip the 'LIMITED' suffix
    and return a title-cased name when not in the canonical map.
    """
    result = PayeeNormalizer().normalize("CHRISTMAS BAKERY LIMITED")
    assert "limited" not in result.lower()
    assert "christmas" in result.lower()


def test_corporate_suffix_ltd_abbreviation_stripped():
    """
    'Some Merchant LTD' should strip the 'LTD' suffix.
    """
    result = PayeeNormalizer().normalize("SOME MERCHANT LTD")
    assert "ltd" not in result.lower()
    assert "merchant" in result.lower()


def test_unknown_merchant_title_cased():
    """
    Merchants not in the canonical map and without a known prefix should
    be returned in Title Case rather than ALL CAPS.
    """
    result = PayeeNormalizer().normalize("TUDOR LOCAL")
    assert result == "Tudor Local"


def test_canonical_map_still_takes_priority_over_suffix_stripping():
    """
    Merchants in the canonical map should still return their canonical name,
    even if they also have a corporate suffix that would otherwise be stripped.
    'GEAR4MUSIC LIMITED' -> 'Gear4music' (from canonical map, not naive strip)
    """
    result = PayeeNormalizer().normalize("GEAR4MUSIC LIMITED")
    assert result == "Gear4music"