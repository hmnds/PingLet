"use client";

import { Layout } from "@/components/layout/Layout";
import { DigestCard } from "@/components/digests/DigestCard";
import { Button } from "@/components/ui/button";
import { useDigests, useRunDigest } from "@/hooks/useDigests";
import { Plus } from "lucide-react";
import { useState } from "react";

export default function DigestsPage() {
  const { data: digests, isLoading } = useDigests();
  const runDigest = useRunDigest();
  const [isRunning, setIsRunning] = useState(false);

  const handleRunDigest = async () => {
    try {
      setIsRunning(true);
      await runDigest.mutateAsync(undefined);
    } catch (error) {
      console.error("Failed to run digest", error);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Digests</h1>
            <p className="text-gray-600 mt-2">View your digest history</p>
          </div>
          <Button onClick={handleRunDigest} disabled={isRunning || runDigest.isPending}>
            <Plus className="h-4 w-4 mr-2" />
            {isRunning || runDigest.isPending ? "Generating..." : "Generate New Digest"}
          </Button>
        </div>

        {isLoading ? (
          <div className="text-gray-600">Loading...</div>
        ) : digests && digests.length > 0 ? (
          <div className="grid gap-6">
            {digests.map((digest) => (
              <DigestCard key={digest.id} digest={digest} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No digests yet. Generate one to get started.</p>
          </div>
        )}
      </div>
    </Layout>
  );
}

