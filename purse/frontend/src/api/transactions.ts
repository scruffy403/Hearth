import { apiClient } from "./client";
import type { Transaction, TransactionFilters, CategoryUpdatePayload } from "../types/transaction";

export const transactionsApi = {
  list: async (filters: TransactionFilters = {}): Promise<Transaction[]> => {
    const { data } = await apiClient.get<Transaction[]>("/transactions", {
      params: filters,
    });
    return data;
  },

  get: async (id: string): Promise<Transaction> => {
    const { data } = await apiClient.get<Transaction>(`/transactions/${id}`);
    return data;
  },

  updateCategory: async (
    id: string,
    payload: CategoryUpdatePayload
  ): Promise<Transaction> => {
    const { data } = await apiClient.patch<Transaction>(
      `/transactions/${id}/category`,
      payload
    );
    return data;
  },

  lowConfidence: async (): Promise<Transaction[]> => {
    const { data } = await apiClient.get<Transaction[]>(
      "/transactions/low-confidence"
    );
    return data;
  },
};
