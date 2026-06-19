import { apiClient } from "./client";
import type { MLTrainingLog } from "../types/ml";

export const mlApi = {
  trainingLog: async (): Promise<MLTrainingLog[]> => {
    const { data } = await apiClient.get<MLTrainingLog[]>("/ml/training-log");
    return data;
  },

  retrain: async (): Promise<{ success: boolean; message: string; sample_count: number }> => {
    const { data } = await apiClient.post("/ml/retrain");
    return data;
  },
};
