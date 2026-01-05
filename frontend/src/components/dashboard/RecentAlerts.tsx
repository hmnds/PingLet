"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAlerts } from "@/hooks/useAlerts";
import { formatRelativeTime } from "@/lib/utils/date";
import Link from "next/link";

export function RecentAlerts() {
  const { data: alerts, isLoading } = useAlerts({ limit: 5 });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-gray-500">Loading...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Alerts</CardTitle>
      </CardHeader>
      <CardContent>
        {!alerts || alerts.length === 0 ? (
          <p className="text-gray-500">No alerts yet</p>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="border-b border-gray-200 pb-4 last:border-0">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900">
                        Rule #{alert.rule_id}
                      </span>
                      <span className="text-xs text-gray-500">•</span>
                      <span className="text-xs text-gray-500">{alert.trigger_type}</span>
                      {alert.score && (
                        <>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-500">Score: {alert.score.toFixed(2)}</span>
                        </>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{formatRelativeTime(alert.sent_at)}</p>
                  </div>
                </div>
              </div>
            ))}
            <Link
              href="/alerts"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View all alerts →
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

