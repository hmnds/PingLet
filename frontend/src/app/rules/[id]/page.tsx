"use client";

import { use } from "react";
import { Layout } from "@/components/layout/Layout";
import { RuleForm } from "@/components/rules/RuleForm";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRule, useUpdateRule, useDeleteRule } from "@/hooks/useRules";
import { useRouter } from "next/navigation";
import type { AlertRuleUpdate } from "@/lib/types";

export default function RuleDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const ruleId = parseInt(id);
  const router = useRouter();
  const { data: rule, isLoading } = useRule(ruleId);
  const updateRule = useUpdateRule();
  const deleteRule = useDeleteRule();

  if (isLoading) {
    return (
      <Layout>
        <div className="text-gray-600">Loading...</div>
      </Layout>
    );
  }

  if (!rule) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-500">Rule not found</p>
          <Button onClick={() => router.push("/rules")} className="mt-4">
            Back to Rules
          </Button>
        </div>
      </Layout>
    );
  }

  const handleSubmit = async (data: AlertRuleUpdate) => {
    try {
      await updateRule.mutateAsync({ id: ruleId, data });
      router.push("/rules");
    } catch (error) {
      console.error("Failed to update rule", error);
    }
  };

  const handleDelete = async () => {
    if (confirm("Are you sure you want to delete this rule?")) {
      try {
        await deleteRule.mutateAsync(ruleId);
        router.push("/rules");
      } catch (error) {
        console.error("Failed to delete rule", error);
      }
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{rule.name}</h1>
            <p className="text-gray-600 mt-2">Edit alert rule</p>
          </div>
          <Button variant="destructive" onClick={handleDelete} disabled={deleteRule.isPending}>
            Delete
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Rule Details</CardTitle>
          </CardHeader>
          <CardContent>
            <RuleForm
              rule={rule}
              onSubmit={handleSubmit}
              onCancel={() => router.push("/rules")}
              isLoading={updateRule.isPending}
            />
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}

