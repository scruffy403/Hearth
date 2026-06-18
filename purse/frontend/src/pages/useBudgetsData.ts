import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { categoriesApi } from "../api/categories";
import { budgetsApi } from "../api/budgets";

export interface BudgetRowData {
  category: string;
  hasBudget: boolean;
  budgeted: number;
  actual: number;
  remaining: number;
}

function getCurrentMonthBounds() {
  const now = new Date();
  const from = new Date(now.getFullYear(), now.getMonth(), 1);
  return { from_date: from.toISOString().slice(0, 10) };
}

/**
 * Combines the full dashboard category list with vs-actual data, so
 * categories without a BudgetConfig still appear (with hasBudget: false)
 * rather than being invisible just because no budget row exists for them.
 * Actual spend for unbudgeted categories comes from the categories
 * summary, so "no budget set" doesn't also mean "no spend visible".
 */
export function useBudgetRows() {
  const { from_date } = getCurrentMonthBounds();

  const categoriesQuery = useQuery({
    queryKey: ["categories", "list"],
    queryFn: () => categoriesApi.list(),
    staleTime: Infinity,
  });

  const summaryQuery = useQuery({
    queryKey: ["categories", "summary", from_date],
    queryFn: () => categoriesApi.summary(from_date),
  });

  const vsActualQuery = useQuery({
    queryKey: ["budgets", "vs-actual"],
    queryFn: () => budgetsApi.vsActual(),
  });

  const isLoading =
    categoriesQuery.isLoading || vsActualQuery.isLoading || summaryQuery.isLoading;

  const rows: BudgetRowData[] = (categoriesQuery.data ?? []).map((category) => {
    const existing = vsActualQuery.data?.find((b) => b.category === category);
    if (existing) {
      return {
        category,
        hasBudget: true,
        budgeted: existing.budgeted,
        actual: existing.actual,
        remaining: existing.remaining,
      };
    }

    const summaryRow = summaryQuery.data?.find((s) => s.category === category);
    return {
      category,
      hasBudget: false,
      budgeted: 0,
      actual: summaryRow?.total ?? 0,
      remaining: 0,
    };
  });

  return { rows, isLoading };
}

export function useUpsertBudget() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ category, monthlyAmount }: { category: string; monthlyAmount: number }) =>
      budgetsApi.upsert(category, { mode: "manual", monthly_amount: monthlyAmount }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
    },
  });
}
