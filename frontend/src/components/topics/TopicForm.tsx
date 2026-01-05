"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { TopicCreate } from "@/lib/types";

const topicSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().min(1, "Description is required"),
  threshold: z.number().min(0).max(1).default(0.7),
});

type TopicFormData = z.infer<typeof topicSchema>;

interface TopicFormProps {
  onSubmit: (data: TopicCreate) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function TopicForm({ onSubmit, onCancel, isLoading }: TopicFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TopicFormData>({
    resolver: zodResolver(topicSchema),
    defaultValues: {
      threshold: 0.7,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Name *
        </label>
        <Input id="name" {...register("name")} placeholder="Crypto News" />
        {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>}
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description *
        </label>
        <textarea
          id="description"
          {...register("description")}
          rows={4}
          className="flex w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
          placeholder="Posts about cryptocurrency, blockchain, and digital assets"
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="threshold" className="block text-sm font-medium text-gray-700 mb-1">
          Similarity Threshold
        </label>
        <Input
          id="threshold"
          type="number"
          step="0.01"
          min="0"
          max="1"
          {...register("threshold", { valueAsNumber: true })}
        />
        {errors.threshold && (
          <p className="mt-1 text-sm text-red-600">{errors.threshold.message}</p>
        )}
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Creating..." : "Create Topic"}
        </Button>
      </div>
    </form>
  );
}

