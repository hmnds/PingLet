import { apiClient } from "./client";

export interface Citation {
  index: number;
  url: string;
  text_preview: string;
}

export interface ChatMessage {
  question: string;
  answer: string;
  citations: Citation[];
  posts: any[];
}

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  posts: any[];
}

export const chatApi = {
  chat: async (question: string): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>("/chat", { question });
    return response.data;
  },
};


