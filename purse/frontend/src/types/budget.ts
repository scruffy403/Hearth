export interface BudgetConfig {
  category_dashboard: string;
  mode: "manual" | "ynab" | "stable";
  monthly_amount: number | null;
}

export interface BudgetVsActual {
  category: string;
  budgeted: number;
  actual: number;
  remaining: number;
}
