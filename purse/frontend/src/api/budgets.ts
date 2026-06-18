import { apiClient } from "./client";
import type { BudgetConfig, BudgetVsActual } from "../types/budget";

export const budgetsApi = {
  list: async (): Promise<BudgetConfig[]> => {
    const { data } = await apiClient.get<BudgetConfig[]>("/budgets");
    return data;
  },

  vsActual: async (): Promise<BudgetVsActual[]> => {
    const { data } = await apiClient.get<BudgetVsActual[]>("/budgets/vs-actual");
    return data;
  },

  upsert: async (
    category: string,
    payload: { mode: string; monthly_amount: number | null }
  ): Promise<BudgetConfig> => {
    const { data } = await apiClient.put<BudgetConfig>(`/budgets/${category}`, payload);
    return data;
  },
};
