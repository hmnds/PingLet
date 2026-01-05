"use client";

import { Layout } from "@/components/layout/Layout";
import { RuleForm } from "@/components/rules/RuleForm";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCreateRule } from "@/hooks/useRules";
import { useRouter } from "next/navigation";
import type { AlertRuleCreate, AlertRuleUpdate } from "@/lib/types";

export default function NewRulePage() {
  const router = useRouter();
  const createRule = useCreateRule();

  const handleSubmit = async (data: AlertRuleCreate | AlertRuleUpdate) => {
    try {
      await createRule.mutateAsync(data as AlertRuleCreate);
      router.push("/rules");
    } catch (error) {
      console.error("Failed to create rule", error);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create Alert Rule</h1>
          <p className="text-gray-600 mt-2">Create a new alert rule</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Rule Details</CardTitle>
          </CardHeader>
          <CardContent>
            <RuleForm
              onSubmit={handleSubmit}
              onCancel={() => router.push("/rules")}
              isLoading={createRule.isPending}
            />
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}

