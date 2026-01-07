"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AlertLog } from "@/lib/types";
import { formatRelativeTime } from "@/lib/utils/date";
import Link from "next/link";

interface AlertCardProps {
  alert: AlertLog;
}

export function AlertCard({ alert }: AlertCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium text-gray-900">Rule #{alert.rule_id}</span>
              <Badge variant={alert.status === "sent" ? "success" : "destructive"}>
                {alert.status}
              </Badge>
              <Badge variant="default">{alert.trigger_type}</Badge>
              {alert.score && (
                <span className="text-xs text-gray-500">Score: {alert.score.toFixed(2)}</span>
              )}
            </div>
            <div className="text-sm text-gray-600 mb-2">
              Post ID: {alert.post_id}
            </div>
            <p className="text-xs text-gray-400">{formatRelativeTime(alert.sent_at)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


