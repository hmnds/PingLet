"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useRules } from "@/hooks/useRules";
import { useTopics } from "@/hooks/useTopics";
import type { AlertRule, AlertRuleCreate, AlertRuleUpdate } from "@/lib/types";

const ruleSchema = z.object({
  name: z.string().min(1, "Name is required"),
  enabled: z.boolean(),
  keywords: z.array(z.string()).optional().nullable(),
  topic_ids: z.array(z.number()).optional().nullable(),
  allowed_author_ids: z.array(z.number()).optional().nullable(),
  similarity_threshold: z.number().min(0).max(1),
  cooldown_minutes: z.number().min(0),
  channel: z.string(),
});

type RuleFormData = z.infer<typeof ruleSchema>;

interface RuleFormProps {
  rule?: AlertRule;
  onSubmit: (data: AlertRuleCreate | AlertRuleUpdate) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function RuleForm({ rule, onSubmit, onCancel, isLoading }: RuleFormProps) {
  const [keywords, setKeywords] = useState<string>(rule?.keywords?.join(", ") || "");
  const [selectedTopics, setSelectedTopics] = useState<number[]>(rule?.topic_ids || []);
  const { data: topics } = useTopics();
  const { data: rules } = useRules();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<RuleFormData>({
    resolver: zodResolver(ruleSchema),
    defaultValues: rule
      ? {
          name: rule.name,
          enabled: rule.enabled,
          keywords: rule.keywords,
          topic_ids: rule.topic_ids,
          allowed_author_ids: rule.allowed_author_ids,
          similarity_threshold: rule.similarity_threshold,
          cooldown_minutes: rule.cooldown_minutes,
          channel: rule.channel,
        }
      : {
          enabled: true,
          similarity_threshold: 0.7,
          cooldown_minutes: 60,
          channel: "log",
        },
  });

  const handleFormSubmit = async (data: RuleFormData) => {
    const keywordsArray = keywords
      .split(",")
      .map((k) => k.trim())
      .filter((k) => k.length > 0);

    const submitData = {
      ...data,
      keywords: keywordsArray.length > 0 ? keywordsArray : null,
      topic_ids: selectedTopics.length > 0 ? selectedTopics : null,
    };

    await onSubmit(submitData);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Name *
        </label>
        <Input id="name" {...register("name")} placeholder="My Alert Rule" />
        {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>}
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="enabled"
          {...register("enabled")}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="enabled" className="ml-2 text-sm text-gray-700">
          Enabled
        </label>
      </div>

      <div>
        <label htmlFor="keywords" className="block text-sm font-medium text-gray-700 mb-1">
          Keywords (comma-separated)
        </label>
        <Input
          id="keywords"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="bitcoin, crypto, AI"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Topics</label>
        <div className="space-y-2 max-h-32 overflow-y-auto border border-gray-200 rounded-md p-2">
          {topics?.map((topic) => (
            <div key={topic.id} className="flex items-center">
              <input
                type="checkbox"
                id={`topic-${topic.id}`}
                checked={selectedTopics.includes(topic.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedTopics([...selectedTopics, topic.id]);
                  } else {
                    setSelectedTopics(selectedTopics.filter((id) => id !== topic.id));
                  }
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor={`topic-${topic.id}`} className="ml-2 text-sm text-gray-700">
                {topic.name}
              </label>
            </div>
          ))}
          {(!topics || topics.length === 0) && (
            <p className="text-sm text-gray-500">No topics available</p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="similarity_threshold" className="block text-sm font-medium text-gray-700 mb-1">
          Similarity Threshold
        </label>
        <Input
          id="similarity_threshold"
          type="number"
          step="0.01"
          min="0"
          max="1"
          {...register("similarity_threshold", { valueAsNumber: true })}
        />
        {errors.similarity_threshold && (
          <p className="mt-1 text-sm text-red-600">{errors.similarity_threshold.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="cooldown_minutes" className="block text-sm font-medium text-gray-700 mb-1">
          Cooldown (minutes)
        </label>
        <Input
          id="cooldown_minutes"
          type="number"
          min="0"
          {...register("cooldown_minutes", { valueAsNumber: true })}
        />
        {errors.cooldown_minutes && (
          <p className="mt-1 text-sm text-red-600">{errors.cooldown_minutes.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="channel" className="block text-sm font-medium text-gray-700 mb-1">
          Channel
        </label>
        <select
          id="channel"
          {...register("channel")}
          className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm"
        >
          <option value="log">Log</option>
          <option value="email">Email</option>
          <option value="telegram">Telegram</option>
          <option value="webhook">Webhook</option>
        </select>
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Saving..." : rule ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}

