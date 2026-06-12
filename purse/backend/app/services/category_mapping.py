"""
Maps YNAB category names to Hearth Purse dashboard categories.

Dashboard categories are intentionally broader than YNAB categories —
YNAB holds the household-specific detail, the dashboard shows the
high-level spending picture.

When new YNAB categories are created, add them here. Unmapped categories
fall through to the ML pipeline which will attempt to categorise them
based on merchant name patterns.
"""
from __future__ import annotations

YNAB_TO_DASHBOARD: dict[str, str] = {
    # --- Groceries ---
    "Groceries": "Groceries",
    "Kids Snacks": "Groceries",

    # --- Eating Out ---
    "Dining Out": "Eating Out",

    # --- Transport ---
    # All vehicle and travel costs — fuel, insurance, tax, maintenance, rail
    "Transportation": "Transport",
    "Auto Maintenance": "Transport",
    "DVLA- car tax": "Transport",
    "Car insurance": "Transport",
    "Fuel": "Transport",
    "StageCoach": "Transport",
    "Auto Loan": "Transport",

    # --- Shopping ---
    "Clothing": "Shopping",
    "Home Improvement": "Shopping",
    "Stuff I Forgot to Budget For": "Shopping",
    "Hobbies": "Shopping",
    "Electronics": "Shopping",
    "Electronic purchases": "Shopping",
    "Home Maintenance": "Shopping",
    "Home Addition": "Shopping",
    "National Trust": "Shopping",

    # --- Bills & Utilities ---
    "Cell Phones": "Bills & Utilities",
    "Mortgage": "Bills & Utilities",
    "Life insurance": "Bills & Utilities",
    "Cleaning": "Bills & Utilities",
    "Internet": "Bills & Utilities",
    "Electricity": "Bills & Utilities",
    "Gas": "Bills & Utilities",
    "Water": "Bills & Utilities",
    "Council Tax": "Bills & Utilities",
    "Electric": "Bills & Utilities",
    "Window Cleaning": "Bills & Utilities",
    "Home Insurance": "Bills & Utilities",

    # --- Subscriptions ---
    "Streaming": "Subscriptions",
    "Software": "Subscriptions",
    "Sync for YNAB": "Subscriptions",

    # --- Personal Spending ---
    # Individual monthly allowances — each person's own discretionary money
    "Naomi": "Personal Spending",
    "JD": "Personal Spending",

    # --- Family ---
    "Swimming Lessons": "Family",
    "Daycare": "Family",
    "Music lessons": "Family",
    "Kids Activities": "Family",
    "School": "Family",
    "Gymnastics": "Family",
    "Ashlyn Trips": "Family",
    "School outfits": "Family",
    "Visa Applications": "Family",

    # --- Pets ---
    "Pets": "Pets",
    "Dog Walking": "Pets",
    "Vet": "Pets",

    # --- Health ---
    "Counseling": "Health",
    "Medical": "Health",
    "Dentist": "Health",
    "Pharmacy": "Health",
    "Gym": "Health",
    "Prescription": "Health",
    "Medical expenses": "Health",
    "Personal care": "Health",
    "23&me": "Health",

    # --- Giving & Charity ---
    "Giving": "Giving",
    "UNICEF": "Giving",
    "Charity": "Giving",

    # --- Gifts ---
    "Gifts": "Gifts",

    # --- Holidays ---
    "Vacation": "Holidays",
    "Travel": "Holidays",

    # --- Savings ---
    "Monthly Saving": "Savings",
    "Emergency Fund": "Savings",

    # --- Income ---
    "Inflow: Ready to Assign": "Income",
}

# Dashboard categories in display order
# Used by the frontend for consistent ordering in charts and tables
DASHBOARD_CATEGORIES: list[str] = [
    "Groceries",
    "Eating Out",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Subscriptions",
    "Personal Spending",
    "Family",
    "Pets",
    "Health",
    "Giving",
    "Gifts",
    "Holidays",
    "Savings",
    "Income",
    "Other",
]


def map_ynab_to_dashboard(ynab_category: str) -> str | None:
    """
    Map a YNAB category name to a dashboard category.

    Returns None if no mapping exists — the caller should fall through
    to the ML pipeline or leave as 'Other'.

    Args:
        ynab_category: Category name as it appears in YNAB

    Returns:
        Dashboard category name, or None if unmapped
    """
    return YNAB_TO_DASHBOARD.get(ynab_category)


def get_dashboard_categories() -> list[str]:
    """Return all dashboard categories in display order."""
    return DASHBOARD_CATEGORIES.copy()