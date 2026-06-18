export interface Transaction {
  id: string;
  date: string; // ISO date string, e.g. "2024-01-15"
  amount: number; // negative = expense, positive = income
  currency: string;
  merchant_raw: string;
  merchant_clean: string | null;
  category_ynab: string | null;
  category_dashboard: string | null;
  category_source: "ynab" | "keyword" | "ml" | "manual_override" | "amount" | "other" | null;
  ml_confidence: number | null;
  ynab_approved: boolean;
  is_transfer: boolean;
  notes: string | null;
}

export interface TransactionFilters {
  from_date?: string;
  to_date?: string;
  categories?: string[];
  limit?: number;
  offset?: number;
}

export interface CategoryUpdatePayload {
  category: string;
  save_as_merchant_rule?: boolean;
}
