import { apiClient } from "./client";
import type { Topic, TopicCreate } from "@/lib/types";

export const topicsApi = {
  list: async (): Promise<Topic[]> => {
    const response = await apiClient.get<Topic[]>("/topics");
    return response.data;
  },

  get: async (id: number): Promise<Topic> => {
    const response = await apiClient.get<Topic>(`/topics/${id}`);
    return response.data;
  },

  create: async (data: TopicCreate): Promise<Topic> => {
    const response = await apiClient.post<Topic>("/topics", data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/topics/${id}`);
  },
};


