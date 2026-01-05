"use client";

import { Layout } from "@/components/layout/Layout";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { RecentAlerts } from "@/components/dashboard/RecentAlerts";
import { RecentDigests } from "@/components/dashboard/RecentDigests";
import { useAccounts } from "@/hooks/useAccounts";
import { useRules } from "@/hooks/useRules";
import { useAlerts } from "@/hooks/useAlerts";
import { Users, AlertTriangle, FileText } from "lucide-react";

export default function DashboardPage() {
  const { data: accounts, isLoading: accountsLoading } = useAccounts();
  const { data: rules, isLoading: rulesLoading } = useRules();
  const { data: alerts, isLoading: alertsLoading } = useAlerts({ limit: 1 });

  return (
    <Layout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Overview of your PingLet account</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCard
            title="Monitored Accounts"
            value={accountsLoading ? "..." : accounts?.length || 0}
            icon={<Users className="h-8 w-8" />}
          />
          <StatsCard
            title="Alert Rules"
            value={rulesLoading ? "..." : rules?.length || 0}
            icon={<AlertTriangle className="h-8 w-8" />}
          />
          <StatsCard
            title="Total Alerts"
            value={alertsLoading ? "..." : alerts?.length || 0}
            icon={<FileText className="h-8 w-8" />}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RecentAlerts />
          <RecentDigests />
        </div>
      </div>
    </Layout>
  );
}
