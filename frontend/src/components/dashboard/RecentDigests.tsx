"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLatestDigest } from "@/hooks/useDigests";
import { formatDate } from "@/lib/utils/date";
import Link from "next/link";

export function RecentDigests() {
  const { data: digest, isLoading } = useLatestDigest();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Latest Digest</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-gray-500">Loading...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Latest Digest</CardTitle>
      </CardHeader>
      <CardContent>
        {!digest ? (
          <p className="text-gray-500">No digests yet</p>
        ) : (
          <div>
            <div className="mb-4">
              <p className="text-sm font-medium text-gray-900">
                {formatDate(digest.digest_date)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Created {formatDate(digest.created_at)}
              </p>
            </div>
            <div className="text-sm text-gray-600 line-clamp-3 mb-4">
              {digest.content_markdown.substring(0, 200)}...
            </div>
            <Link
              href={`/digests/${digest.digest_date}`}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Read full digest →
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

