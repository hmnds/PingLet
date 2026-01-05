"use client";

import { useState } from "react";
import { AlertCard } from "./AlertCard";
import { useAlerts } from "@/hooks/useAlerts";
import { Select } from "@/components/ui/select";
import { useRules } from "@/hooks/useRules";

export function AlertList() {
  const [selectedRuleId, setSelectedRuleId] = useState<number | undefined>();
  const { data: alerts, isLoading, error } = useAlerts({
    limit: 100,
    rule_id: selectedRuleId,
  });
  const { data: rules } = useRules();

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-200 animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load alerts</p>
      </div>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No alerts yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <label htmlFor="rule-filter" className="block text-sm font-medium text-gray-700 mb-2">
          Filter by Rule
        </label>
        <Select
          id="rule-filter"
          value={selectedRuleId || ""}
          onChange={(e) =>
            setSelectedRuleId(e.target.value ? parseInt(e.target.value) : undefined)
          }
          className="w-full md:w-64"
        >
          <option value="">All Rules</option>
          {rules?.map((rule) => (
            <option key={rule.id} value={rule.id}>
              {rule.name}
            </option>
          ))}
        </Select>
      </div>

      <div className="space-y-4">
        {alerts.map((alert) => (
          <AlertCard key={alert.id} alert={alert} />
        ))}
      </div>
    </div>
  );
}

