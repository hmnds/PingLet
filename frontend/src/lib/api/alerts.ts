import { apiClient } from "./client";
import type { AlertLog } from "@/lib/types";

export interface AlertsListParams {
  limit?: number;
  offset?: number;
  rule_id?: number;
}

export const alertsApi = {
  list: async (params?: AlertsListParams): Promise<AlertLog[]> => {
    const response = await apiClient.get<AlertLog[]>("/alerts", { params });
    return response.data;
  },
};


