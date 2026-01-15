import { apiClient } from "./client";

export interface SearchResult {
  id: number;
  x_post_id: string;
  author_id: number;
  created_at: string;
  text: string;
  url: string | null;
  similarity: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
}

export const searchApi = {
  search: async (query: string, limit: number = 10): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>(
      `/search?query=${encodeURIComponent(query)}&limit=${limit}`
    );
    return response.data;
  },
};

