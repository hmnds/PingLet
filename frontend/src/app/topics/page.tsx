"use client";

import { Layout } from "@/components/layout/Layout";
import { TopicList } from "@/components/topics/TopicList";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";

export default function TopicsPage() {
  const router = useRouter();

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Topics</h1>
            <p className="text-gray-600 mt-2">Manage topics for semantic matching</p>
          </div>
          <Button onClick={() => router.push("/topics/new")}>
            <Plus className="h-4 w-4 mr-2" />
            Create Topic
          </Button>
        </div>

        <TopicList />
      </div>
    </Layout>
  );
}


