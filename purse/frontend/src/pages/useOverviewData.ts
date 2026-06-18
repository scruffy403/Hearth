import { useQuery } from "@tanstack/react-query";
import { categoriesApi } from "../api/categories";
import { transactionsApi } from "../api/transactions";
import { budgetsApi } from "../api/budgets";

function getMonthBounds(date = new Date()) {
  const year = date.getFullYear();
  const month = date.getMonth();
  const fromDate = new Date(year, month, 1).toISOString().slice(0, 10);
  const toDate = new Date(year, month + 1, 0).toISOString().slice(0, 10);
  return { fromDate, toDate };
}

export function useCurrentMonthSummary() {
  const { fromDate, toDate } = getMonthBounds();
  return useQuery({
    queryKey: ["categories", "summary", fromDate, toDate],
    queryFn: () => categoriesApi.summary(fromDate, toDate),
  });
}

export function useRecentTransactions(limit = 8) {
  return useQuery({
    queryKey: ["transactions", "recent", limit],
    queryFn: () => transactionsApi.list({ limit }),
  });
}

export function useBudgetsVsActual() {
  return useQuery({
    queryKey: ["budgets", "vs-actual"],
    queryFn: () => budgetsApi.vsActual(),
  });
}
