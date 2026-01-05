"use client";

import { Layout } from "@/components/layout/Layout";
import { AlertList } from "@/components/alerts/AlertList";

export default function AlertsPage() {
  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-600 mt-2">View all triggered alerts</p>
        </div>

        <AlertList />
      </div>
    </Layout>
  );
}

