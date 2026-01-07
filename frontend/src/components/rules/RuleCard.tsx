"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AlertRule } from "@/lib/types";
import { formatDate } from "@/lib/utils/date";
import Link from "next/link";

interface RuleCardProps {
  rule: AlertRule;
}

export function RuleCard({ rule }: RuleCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Link
                href={`/rules/${rule.id}`}
                className="text-lg font-semibold text-gray-900 hover:text-blue-600"
              >
                {rule.name}
              </Link>
              {rule.enabled ? (
                <Badge variant="success">Enabled</Badge>
              ) : (
                <Badge variant="default">Disabled</Badge>
              )}
            </div>
            <div className="space-y-1 text-sm text-gray-600">
              {rule.keywords && rule.keywords.length > 0 && (
                <p>Keywords: {rule.keywords.join(", ")}</p>
              )}
              {rule.topic_ids && rule.topic_ids.length > 0 && (
                <p>Topics: {rule.topic_ids.length} topic(s)</p>
              )}
              <p>Channel: {rule.channel}</p>
            </div>
            <p className="text-xs text-gray-400 mt-3">
              Created {formatDate(rule.created_at)}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


