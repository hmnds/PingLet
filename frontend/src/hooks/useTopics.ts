import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { topicsApi } from "@/lib/api/topics";
import type { TopicCreate } from "@/lib/types";

export function useTopics() {
  return useQuery({
    queryKey: ["topics"],
    queryFn: () => topicsApi.list(),
  });
}

export function useTopic(id: number) {
  return useQuery({
    queryKey: ["topics", id],
    queryFn: () => topicsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateTopic() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TopicCreate) => topicsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["topics"] });
    },
  });
}

export function useDeleteTopic() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => topicsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["topics"] });
    },
  });
}

