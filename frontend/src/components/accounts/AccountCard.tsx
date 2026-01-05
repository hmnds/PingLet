"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { MonitoredAccount } from "@/lib/types";
import { formatDate } from "@/lib/utils/date";
import Link from "next/link";

interface AccountCardProps {
  account: MonitoredAccount;
}

export function AccountCard({ account }: AccountCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Link
                href={`/accounts/${account.id}`}
                className="text-lg font-semibold text-gray-900 hover:text-blue-600"
              >
                @{account.username}
              </Link>
            </div>
            {account.x_user_id && (
              <p className="text-sm text-gray-500 mb-3">X User ID: {account.x_user_id}</p>
            )}
            <div className="flex gap-2 mb-3">
              {account.digest_enabled && (
                <Badge variant="success">Digest Enabled</Badge>
              )}
              {account.alerts_enabled && (
                <Badge variant="success">Alerts Enabled</Badge>
              )}
            </div>
            <p className="text-xs text-gray-400">
              Added {formatDate(account.created_at)}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

