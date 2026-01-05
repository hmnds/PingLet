"use client";

import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { AccountList } from "@/components/accounts/AccountList";
import { AddAccountModal } from "@/components/accounts/AddAccountModal";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export default function AccountsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Monitored Accounts</h1>
            <p className="text-gray-600 mt-2">Manage accounts you want to monitor</p>
          </div>
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Account
          </Button>
        </div>

        <AccountList />

        <AddAccountModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
      </div>
    </Layout>
  );
}

