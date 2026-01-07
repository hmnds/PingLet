"use client";

import { Layout } from "@/components/layout/Layout";
import { TopicForm } from "@/components/topics/TopicForm";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCreateTopic } from "@/hooks/useTopics";
import { useRouter } from "next/navigation";
import type { TopicCreate } from "@/lib/types";

export default function NewTopicPage() {
  const router = useRouter();
  const createTopic = useCreateTopic();

  const handleSubmit = async (data: TopicCreate) => {
    try {
      await createTopic.mutateAsync(data);
      router.push("/topics");
    } catch (error) {
      console.error("Failed to create topic", error);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create Topic</h1>
          <p className="text-gray-600 mt-2">Create a new topic for semantic matching</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Topic Details</CardTitle>
          </CardHeader>
          <CardContent>
            <TopicForm
              onSubmit={handleSubmit}
              onCancel={() => router.push("/topics")}
              isLoading={createTopic.isPending}
            />
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}


