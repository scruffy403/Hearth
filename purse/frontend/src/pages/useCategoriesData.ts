import { useQuery } from "@tanstack/react-query";
import { categoriesApi } from "../api/categories";

function getCurrentMonthBounds() {
  const now = new Date();
  const from = new Date(now.getFullYear(), now.getMonth(), 1);
  return { from_date: from.toISOString().slice(0, 10) };
}

/**
 * Bounds for "the last N calendar months, including the current one".
 * Used to keep the trend chart and the merchants list on the same page
 * describing the same period — see the Family/IT CAREER CHANGE LTD
 * inconsistency this was built to fix.
 */
function getTrailingMonthsBounds(months: number) {
  const now = new Date();
  const from = new Date(now.getFullYear(), now.getMonth() - (months - 1), 1);
  const to = new Date(now.getFullYear(), now.getMonth() + 1, 0); // last day of this month
  return {
    from_date: from.toISOString().slice(0, 10),
    to_date: to.toISOString().slice(0, 10),
  };
}

export function useCategoriesSummary() {
  const { from_date } = getCurrentMonthBounds();
  return useQuery({
    queryKey: ["categories", "summary", from_date],
    queryFn: () => categoriesApi.summary(from_date),
  });
}

export function useCategoryTrends(category: string, months = 6) {
  return useQuery({
    queryKey: ["categories", "trends", category, months],
    queryFn: () => categoriesApi.trends(category, months),
    enabled: !!category,
  });
}

export function useCategoryMerchants(category: string, limit = 10, months = 6) {
  const { from_date, to_date } = getTrailingMonthsBounds(months);
  return useQuery({
    queryKey: ["categories", "merchants", category, limit, from_date, to_date],
    queryFn: () => categoriesApi.merchants(category, limit, from_date, to_date),
    enabled: !!category,
  });
}
