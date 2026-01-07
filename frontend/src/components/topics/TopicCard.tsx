"use client";

import { Card, CardContent } from "@/components/ui/card";
import type { Topic } from "@/lib/types";
import { formatDate } from "@/lib/utils/date";

interface TopicCardProps {
  topic: Topic;
  onDelete?: (id: number) => void;
}

export function TopicCard({ topic, onDelete }: TopicCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{topic.name}</h3>
            <p className="text-sm text-gray-600 mb-3">{topic.description}</p>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>Threshold: {topic.threshold.toFixed(2)}</span>
              <span>Created {formatDate(topic.created_at)}</span>
            </div>
          </div>
          {onDelete && (
            <button
              onClick={() => onDelete(topic.id)}
              className="text-red-600 hover:text-red-700 text-sm font-medium"
            >
              Delete
            </button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}


