"use client";

import { use } from "react";
import { Layout } from "@/components/layout/Layout";
import { DigestViewer } from "@/components/digests/DigestViewer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useDigestByDate } from "@/hooks/useDigests";
import { formatDate } from "@/lib/utils/date";
import { useRouter } from "next/navigation";

export default function DigestDetailPage({ params }: { params: Promise<{ date: string }> }) {
  const { date } = use(params);
  const router = useRouter();
  const { data: digest, isLoading } = useDigestByDate(date);

  if (isLoading) {
    return (
      <Layout>
        <div className="text-gray-600">Loading...</div>
      </Layout>
    );
  }

  if (!digest) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-500">Digest not found</p>
          <Button onClick={() => router.push("/digests")} className="mt-4">
            Back to Digests
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Digest: {formatDate(digest.digest_date)}</h1>
          <p className="text-gray-600 mt-2">Daily summary of monitored accounts</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Content</CardTitle>
          </CardHeader>
          <CardContent>
            <DigestViewer content={digest.content_markdown} />
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}

