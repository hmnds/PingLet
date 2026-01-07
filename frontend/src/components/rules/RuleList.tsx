"use client";

import { RuleCard } from "./RuleCard";
import { useRules } from "@/hooks/useRules";

export function RuleList() {
  const { data: rules, isLoading, error } = useRules();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-gray-200 animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load rules</p>
      </div>
    );
  }

  if (!rules || rules.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No rules yet. Create one to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {rules.map((rule) => (
        <RuleCard key={rule.id} rule={rule} />
      ))}
    </div>
  );
}


