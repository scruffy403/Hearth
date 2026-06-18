export interface CategorySummary {
  category: string;
  total: number; // always positive, magnitude of spend
  transaction_count: number;
}

export interface CategoryTrendPoint {
  month: string; // "YYYY-MM"
  total: number;
}

export interface CategoryMerchant {
  merchant: string;
  total: number;
  transaction_count: number;
}
