"use client";

import { use } from "react";
import { Layout } from "@/components/layout/Layout";
import { useAccount, useUpdateAccount } from "@/hooks/useAccounts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils/date";
import { useRouter } from "next/navigation";

export default function AccountDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const accountId = parseInt(id);
  const router = useRouter();
  const { data: account, isLoading } = useAccount(accountId);
  const updateAccount = useUpdateAccount();

  if (isLoading) {
    return (
      <Layout>
        <div className="text-gray-600">Loading...</div>
      </Layout>
    );
  }

  if (!account) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-500">Account not found</p>
          <Button onClick={() => router.push("/accounts")} className="mt-4">
            Back to Accounts
          </Button>
        </div>
      </Layout>
    );
  }

  const handleToggle = async (field: "digest_enabled" | "alerts_enabled") => {
    try {
      await updateAccount.mutateAsync({
        id: accountId,
        data: { [field]: !account[field] },
      });
    } catch (error) {
      console.error("Failed to update account", error);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">@{account.username}</h1>
          <p className="text-gray-600 mt-2">Account details and settings</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Username</label>
              <p className="text-gray-900 mt-1">@{account.username}</p>
            </div>
            {account.x_user_id && (
              <div>
                <label className="text-sm font-medium text-gray-700">X User ID</label>
                <p className="text-gray-900 mt-1">{account.x_user_id}</p>
              </div>
            )}
            {account.last_seen_post_id && (
              <div>
                <label className="text-sm font-medium text-gray-700">Last Seen Post ID</label>
                <p className="text-gray-900 mt-1 font-mono text-sm">{account.last_seen_post_id}</p>
              </div>
            )}
            <div>
              <label className="text-sm font-medium text-gray-700">Created</label>
              <p className="text-gray-900 mt-1">{formatDate(account.created_at)}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Digest Enabled</label>
                <p className="text-sm text-gray-500 mt-1">
                  Include this account in daily digests
                </p>
              </div>
              <Button
                variant={account.digest_enabled ? "default" : "outline"}
                onClick={() => handleToggle("digest_enabled")}
                disabled={updateAccount.isPending}
              >
                {account.digest_enabled ? "Enabled" : "Disabled"}
              </Button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Alerts Enabled</label>
                <p className="text-sm text-gray-500 mt-1">
                  Send alerts for this account
                </p>
              </div>
              <Button
                variant={account.alerts_enabled ? "default" : "outline"}
                onClick={() => handleToggle("alerts_enabled")}
                disabled={updateAccount.isPending}
              >
                {account.alerts_enabled ? "Enabled" : "Disabled"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}


