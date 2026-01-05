import { useQuery } from "@tanstack/react-query";
import { alertsApi, type AlertsListParams } from "@/lib/api/alerts";

export function useAlerts(params?: AlertsListParams) {
  return useQuery({
    queryKey: ["alerts", params],
    queryFn: () => alertsApi.list(params),
  });
}

