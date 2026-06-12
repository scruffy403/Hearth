from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

from rapidfuzz import process, fuzz
from app.services.category_mapping import map_ynab_to_dashboard


@dataclass
class CategoryResult:
    category: str
    source: str  # 'manual_override' | 'ynab_fuzzy' | 'keyword' | 'other'


class CategorizationService:
    """
    Rule-based categorisation pipeline. Applies categories in priority order:
    1. Manual overrides (merchant_clean -> category)
    2. YNAB fuzzy match (if ynab_payees provided)
    3. Keyword rules
    4. Fallback: 'Other'
    """

    DEFAULT_KEYWORD_RULES: Dict[str, str] = {
        "sainsbury": "Groceries",
        "tesco": "Groceries",
        "asda": "Groceries",
        "aldi": "Groceries",
        "lidl": "Groceries",
        "morrisons": "Groceries",
        "waitrose": "Groceries",
        "restaurant": "Eating Out",
        "coffee": "Eating Out",
        "cafe": "Eating Out",
        "starbucks": "Eating Out",
        "kfc": "Eating Out",
        "mcdonald": "Eating Out",
        "uber": "Transport",
        "bolt": "Transport",
        "trainline": "Transport",
        "rail": "Transport",
        "petrol": "Transport",
        "fuel": "Transport",
        "netflix": "Subscriptions",
        "spotify": "Subscriptions",
        "disney": "Subscriptions",
        "prime video": "Subscriptions",
        "icloud": "Subscriptions",
        "vodafone": "Bills & Utilities",
        "o2": "Bills & Utilities",
        "ee": "Bills & Utilities",
        "water": "Bills & Utilities",
        "octopus energy": "Bills & Utilities",
        "amazon": "Shopping",
    }

    YNAB_FUZZY_THRESHOLD: int = 80

    def __init__(
        self,
        overrides: Dict[str, str],
        keyword_rules: Optional[Dict[str, str]] = None,
        ynab_payees: Optional[list[str]] = None,
        ynab_mapping: Optional[Dict[str, str]] = None,
    ) -> None:
        self.overrides = overrides
        self.keyword_rules = (
            keyword_rules
            if keyword_rules is not None
            else self.DEFAULT_KEYWORD_RULES
        )
        self.ynab_payees = ynab_payees or []
        self.ynab_mapping = ynab_mapping or {}

    def categorize(
            self,
            merchant_clean: str,
            ynab_category: Optional[str] = None,
            amount: float = 0.0,
    ) -> CategoryResult:
        # Income detection
        if amount > 0:
            return CategoryResult(category="Income", source="amount")

        # 0. Direct YNAB category mapping — highest quality signal
        if ynab_category:
            mapped = map_ynab_to_dashboard(ynab_category.strip())
            if mapped:
                return CategoryResult(category=mapped, source="ynab")

        # 1. Manual override
        result = self._apply_manual_override(merchant_clean)
        if result:
            return result

        # 2. YNAB fuzzy match
        result = self._apply_ynab_fuzzy(merchant_clean)
        if result:
            return result

        # 3. Keyword rules
        result = self._apply_keyword_rules(merchant_clean)
        if result:
            return result

        # 4. Fallback
        return CategoryResult(category="Other", source="other")

    def _apply_manual_override(self, merchant: str) -> Optional[CategoryResult]:
        if merchant in self.overrides:
            return CategoryResult(
                category=self.overrides[merchant],
                source="manual_override",
            )
        return None

    def _apply_ynab_fuzzy(self, merchant: str) -> Optional[CategoryResult]:
        if not self.ynab_payees or not merchant:
            return None

        merchant_lower = merchant.lower()
        payees_lower = [p.lower() for p in self.ynab_payees]

        match, score, _ = process.extractOne(
            merchant_lower,
            payees_lower,
            scorer=fuzz.partial_ratio,
        )

        if score >= self.YNAB_FUZZY_THRESHOLD:
            category = self.ynab_mapping.get(match)
            if category:
                return CategoryResult(category=category, source="ynab_fuzzy")

        return None

    def _apply_keyword_rules(self, merchant: str) -> Optional[CategoryResult]:
        merchant_lower = merchant.lower()
        for keyword, category in self.keyword_rules.items():
            if keyword in merchant_lower:
                return CategoryResult(category=category, source="keyword")
        return None