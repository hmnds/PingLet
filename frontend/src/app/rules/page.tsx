"use client";

import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { RuleList } from "@/components/rules/RuleList";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";

export default function RulesPage() {
  const router = useRouter();

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Alert Rules</h1>
            <p className="text-gray-600 mt-2">Manage your alert rules</p>
          </div>
          <Button onClick={() => router.push("/rules/new")}>
            <Plus className="h-4 w-4 mr-2" />
            Create Rule
          </Button>
        </div>

        <RuleList />
      </div>
    </Layout>
  );
}


