"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import type { MonitoredAccount } from "@/lib/types";
import { formatDate } from "@/lib/utils/date";
import { useDeleteAccount } from "@/hooks/useAccounts";
import Link from "next/link";

interface AccountCardProps {
  account: MonitoredAccount;
}

export function AccountCard({ account }: AccountCardProps) {
  const deleteAccount = useDeleteAccount();

  const handleDelete = async () => {
    if (confirm(`Are you sure you want to remove @${account.username}?`)) {
      await deleteAccount.mutateAsync(account.id);
    }
  };

  return (
    <Card className="glass-card hover:-translate-y-1 transition-transform duration-300">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <Link
                href={`/accounts/${account.id}`}
                className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-700 hover:to-indigo-600 transition-all"
              >
                @{account.username}
              </Link>
            </div>
            {account.x_user_id && (
              <div className="flex items-center gap-2 mb-4">
                <span className="px-2 py-1 rounded-md bg-slate-100 text-slate-500 text-xs font-mono">
                  {account.x_user_id}
                </span>
              </div>
            )}
            <div className="flex flex-wrap gap-2 mb-4">
              {account.digest_enabled && (
                <Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-200 border-transparent shadow-none">
                  Digest Enabled
                </Badge>
              )}
              {account.alerts_enabled && (
                <Badge className="bg-indigo-100 text-indigo-700 hover:bg-indigo-200 border-transparent shadow-none">
                  Alerts Enabled
                </Badge>
              )}
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Added {formatDate(account.created_at)}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            disabled={deleteAccount.isPending}
            className="text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-full"
          >
            <Trash2 className="h-5 w-5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}


