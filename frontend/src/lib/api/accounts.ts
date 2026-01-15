import { apiClient } from "./client";
import type { MonitoredAccount, MonitoredAccountCreate, MonitoredAccountUpdate } from "@/lib/types";

export const accountsApi = {
  list: async (): Promise<MonitoredAccount[]> => {
    const response = await apiClient.get<MonitoredAccount[]>("/accounts");
    return response.data;
  },

  get: async (id: number): Promise<MonitoredAccount> => {
    const response = await apiClient.get<MonitoredAccount>(`/accounts/${id}`);
    return response.data;
  },

  create: async (data: MonitoredAccountCreate): Promise<MonitoredAccount> => {
    const response = await apiClient.post<MonitoredAccount>("/accounts", data);
    return response.data;
  },

  update: async (id: number, data: MonitoredAccountUpdate): Promise<MonitoredAccount> => {
    const response = await apiClient.patch<MonitoredAccount>(`/accounts/${id}`, data);
    return response.data;
  },

  resolve: async (id: number): Promise<MonitoredAccount> => {
    const response = await apiClient.post<MonitoredAccount>(`/accounts/${id}/resolve`);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/accounts/${id}`);
  },
};
