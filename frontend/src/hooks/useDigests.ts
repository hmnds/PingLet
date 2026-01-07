import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { digestsApi } from "@/lib/api/digests";

export function useLatestDigest() {
  return useQuery({
    queryKey: ["digests", "latest"],
    queryFn: () => digestsApi.getLatest(),
  });
}

export function useDigestByDate(date: string) {
  return useQuery({
    queryKey: ["digests", date],
    queryFn: () => digestsApi.getByDate(date),
    enabled: !!date,
  });
}

export function useRunDigest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (digestDate?: string) => digestsApi.run(digestDate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["digests"] });
    },
  });
}


