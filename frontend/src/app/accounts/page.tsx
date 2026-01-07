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
            <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-gray-900 via-gray-700 to-gray-800 pb-2">
              Monitored Accounts
            </h1>
            <p className="text-lg text-slate-600">Manage accounts you want to monitor</p>
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


