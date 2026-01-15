import { apiClient } from "./client";
import type { Digest } from "@/lib/types";

export const digestsApi = {
  list: async (): Promise<Digest[]> => {
    const response = await apiClient.get<Digest[]>("/digests/");
    return response.data;
  },

  getLatest: async (): Promise<Digest> => {
    const response = await apiClient.get<Digest>("/digests/latest");
    return response.data;
  },

  getByDate: async (date: string): Promise<Digest> => {
    const response = await apiClient.get<Digest>(`/digests/${date}`);
    return response.data;
  },

  run: async (digestDate?: string): Promise<Digest> => {
    const response = await apiClient.post<Digest>("/digests/run", {
      digest_date: digestDate,
    });
    return response.data;
  },
};


