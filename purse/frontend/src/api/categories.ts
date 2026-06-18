import { apiClient } from "./client";
import type { CategorySummary, CategoryTrendPoint, CategoryMerchant } from "../types/category";

export const categoriesApi = {
  list: async (): Promise<string[]> => {
    const { data } = await apiClient.get<string[]>("/categories");
    return data;
  },

  summary: async (fromDate?: string, toDate?: string): Promise<CategorySummary[]> => {
    const { data } = await apiClient.get<CategorySummary[]>("/categories/summary", {
      params: { from_date: fromDate, to_date: toDate },
    });
    return data;
  },

  trends: async (category: string, months = 12): Promise<CategoryTrendPoint[]> => {
    const { data } = await apiClient.get<CategoryTrendPoint[]>("/categories/trends", {
      params: { category, months },
    });
    return data;
  },

  merchants: async (
    category: string,
    limit = 10,
    fromDate?: string,
    toDate?: string
  ): Promise<CategoryMerchant[]> => {
    const { data } = await apiClient.get<CategoryMerchant[]>("/categories/merchants", {
      params: { category, limit, from_date: fromDate, to_date: toDate },
    });
    return data;
  },
};
