import { apiClient } from "./client";
import type { AlertRule, AlertRuleCreate, AlertRuleUpdate } from "@/lib/types";

export const rulesApi = {
  list: async (): Promise<AlertRule[]> => {
    const response = await apiClient.get<AlertRule[]>("/rules");
    return response.data;
  },

  get: async (id: number): Promise<AlertRule> => {
    const response = await apiClient.get<AlertRule>(`/rules/${id}`);
    return response.data;
  },

  create: async (data: AlertRuleCreate): Promise<AlertRule> => {
    const response = await apiClient.post<AlertRule>("/rules", data);
    return response.data;
  },

  update: async (id: number, data: AlertRuleUpdate): Promise<AlertRule> => {
    const response = await apiClient.patch<AlertRule>(`/rules/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/rules/${id}`);
  },
};


