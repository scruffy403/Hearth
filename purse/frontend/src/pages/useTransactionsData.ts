import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { transactionsApi } from "../api/transactions";
import { categoriesApi } from "../api/categories";
import type { CategoryUpdatePayload } from "../types/transaction";

export type DateRangeFilter =
  | "this_month"
  | "last_month"
  | "last_30_days"
  | "last_6_months"
  | "all";

export function getDateRangeBounds(range: DateRangeFilter): {
  from_date?: string;
  to_date?: string;
} {
  const now = new Date();

  if (range === "this_month") {
    const from = new Date(now.getFullYear(), now.getMonth(), 1);
    return { from_date: from.toISOString().slice(0, 10) };
  }

  if (range === "last_month") {
    const from = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const to = new Date(now.getFullYear(), now.getMonth(), 0);
    return {
      from_date: from.toISOString().slice(0, 10),
      to_date: to.toISOString().slice(0, 10),
    };
  }

  if (range === "last_30_days") {
    const from = new Date(now);
    from.setDate(from.getDate() - 30);
    return { from_date: from.toISOString().slice(0, 10) };
  }

  if (range === "last_6_months") {
    // Same calculation as the Categories trend window, so a drill-down
    // link from there lands on a matching range.
    const from = new Date(now.getFullYear(), now.getMonth() - 5, 1);
    return { from_date: from.toISOString().slice(0, 10) };
  }

  return {};
}

const PAGE_SIZE = 500;

interface UseTransactionsListOptions {
  dateRange: DateRangeFilter;
  categories: string[];
  lowConfidenceOnly: boolean;
  merchant?: string;
  offset?: number;
}

export function useTransactionsList({
  dateRange,
  categories,
  lowConfidenceOnly,
  merchant,
  offset = 0,
}: UseTransactionsListOptions) {
  const dateBounds = getDateRangeBounds(dateRange);

  return useQuery({
    queryKey: ["transactions", "list", dateRange, categories, lowConfidenceOnly, merchant, offset],
    queryFn: async () => {
      const results = lowConfidenceOnly
        ? await transactionsApi.lowConfidence()
        : await transactionsApi.list({
            ...dateBounds,
            categories: categories.length > 0 ? categories : undefined,
            limit: PAGE_SIZE,
            offset,
          });

      // Merchant filtering is done client-side rather than via a new
      // backend param — at these volumes it's not worth the extra API surface.
      const filtered = merchant
        ? results.filter((tx) => (tx.merchant_clean ?? tx.merchant_raw) === merchant)
        : results;

      return {
        transactions: filtered,
        hasMore: results.length === PAGE_SIZE && dateRange === "all",
      };
    },
  });
}

export { PAGE_SIZE };

export function useAllCategories() {
  return useQuery({
    queryKey: ["categories", "list"],
    queryFn: () => categoriesApi.list(),
    staleTime: Infinity, // category list essentially never changes
  });
}

export function useUpdateTransactionCategory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: CategoryUpdatePayload;
    }) => transactionsApi.updateCategory(id, payload),
    onSuccess: () => {
      // Invalidate everything derived from transaction data — categories
      // summary, budgets vs actual, and the lists themselves all need
      // to reflect the change.
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
    },
  });
}
