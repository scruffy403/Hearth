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