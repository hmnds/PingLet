"use client";

import { TopicCard } from "./TopicCard";
import { useTopics, useDeleteTopic } from "@/hooks/useTopics";

export function TopicList() {
  const { data: topics, isLoading, error } = useTopics();
  const deleteTopic = useDeleteTopic();

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this topic?")) {
      try {
        await deleteTopic.mutateAsync(id);
      } catch (error) {
        console.error("Failed to delete topic", error);
      }
    }
  };

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
        <p className="text-red-600">Failed to load topics</p>
      </div>
    );
  }

  if (!topics || topics.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No topics yet. Create one to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {topics.map((topic) => (
        <TopicCard key={topic.id} topic={topic} onDelete={handleDelete} />
      ))}
    </div>
  );
}

