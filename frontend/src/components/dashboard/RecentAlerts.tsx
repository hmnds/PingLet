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
    <Card className="glass-card flex flex-col h-full">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold text-slate-800">Recent Alerts</CardTitle>
      </CardHeader>
      <CardContent className="flex-1">
        {!alerts || alerts.length === 0 ? (
          <div className="text-center py-8 text-slate-500 bg-slate-50/50 rounded-xl border border-slate-100">
            <p>No alerts triggered yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div key={alert.id} className="group p-3 rounded-xl bg-white/50 border border-slate-100 hover:border-indigo-100 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-indigo-50 text-indigo-600 text-xs font-bold">
                        #{alert.rule_id}
                      </span>
                      <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full capitalize">
                        {alert.trigger_type}
                      </span>
                      {alert.score && (
                        <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                          {(alert.score * 100).toFixed(0)}% Match
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 pl-8">{formatRelativeTime(alert.sent_at)}</p>
                  </div>
                </div>
              </div>
            ))}
            <div className="pt-2">
              <Link
                href="/alerts"
                className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors group"
              >
                View all alerts
                <span className="ml-1 group-hover:translate-x-1 transition-transform">→</span>
              </Link>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}


