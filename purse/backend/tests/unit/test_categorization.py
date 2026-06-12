from app.services.categorization import CategorizationService, CategoryResult

def test_manual_override_takes_priority():
    service = CategorizationService(
        overrides={"Tesco": "Groceries"},
        keyword_rules={}
    )
    result = service.categorize("Tesco", ynab_category=None)
    assert result.category == "Groceries"
    assert result.source == "manual_override"

def test_keyword_rule_applies_when_no_override():
    service = CategorizationService(
        overrides={},
        keyword_rules={"tesco": "Groceries"}
    )
    result = service.categorize("Tesco", ynab_category=None)
    assert result.category == "Groceries"
    assert result.source == "keyword"

def test_returns_other_when_no_match():
    service = CategorizationService(overrides={}, keyword_rules={})
    result = service.categorize("Unknown Merchant", ynab_category=None)
    assert result.category == "Other"

def test_income_detected_by_positive_amount():
    service = CategorizationService(overrides={}, keyword_rules={})
    result = service.categorize("Nationwide", amount=3850.00)
    assert result.category == "Income"
    assert result.source == "amount"

def test_keyword_matching_is_case_insensitive():
    service = CategorizationService(
        overrides={},
        keyword_rules={"tesco": "Groceries"}
    )
    result = service.categorize("tesco express")
    assert result.category == "Groceries"

def test_override_takes_priority_over_keyword():
    service = CategorizationService(
        overrides={"Tesco": "Special"},
        keyword_rules={"tesco": "Groceries"}
    )
    result = service.categorize("Tesco")
    assert result.category == "Special"
    assert result.source == "manual_override"

def test_ynab_fuzzy_match():
    service = CategorizationService(
        overrides={},
        keyword_rules={},
        ynab_payees=["tesco superstore"],
        ynab_mapping={"tesco superstore": "Groceries"}
    )
    result = service.categorize("Tesco")
    assert result.category == "Groceries"
    assert result.source == "ynab_fuzzy"

def test_ynab_category_mapping_takes_priority_over_keywords():
    service = CategorizationService(
        overrides={},
        keyword_rules={"tesco": "Groceries"}
    )
    # YNAB says Dining Out, keyword would say Groceries
    # YNAB mapping should win
    result = service.categorize(
        merchant_clean="Tesco",
        ynab_category="Dining Out",
        amount=0.0
    )
    assert result.category == "Eating Out"
    assert result.source == "ynab"

def test_unmapped_ynab_category_falls_through_to_keywords():
    service = CategorizationService(
        overrides={},
        keyword_rules={"tesco": "Groceries"}
    )
    result = service.categorize(
        merchant_clean="Tesco",
        ynab_category="Some Unmapped Category",
        amount=0.0
    )
    assert result.category == "Groceries"
    assert result.source == "keyword"

def test_ynab_category_with_trailing_space_is_mapped():
    """
    Regression test: YNAB category names sometimes have trailing whitespace.
    The mapping must strip before lookup to avoid silent misses.
    """
    service = CategorizationService(overrides={}, keyword_rules={})
    result = service.categorize(
        merchant_clean="USAA Insurance",
        ynab_category="Car insurance ",  # trailing space
        amount=-96.84
    )
    assert result.category == "Transport"
    assert result.source == "ynab"