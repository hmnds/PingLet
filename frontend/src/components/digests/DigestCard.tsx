"use client";

import { Card, CardContent } from "@/components/ui/card";
import type { Digest } from "@/lib/types";
import { formatDate } from "@/lib/utils/date";
import Link from "next/link";

interface DigestCardProps {
  digest: Digest;
}

export function DigestCard({ digest }: DigestCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <Link
              href={`/digests/${digest.digest_date}`}
              className="text-lg font-semibold text-gray-900 hover:text-blue-600 block mb-2"
            >
              {formatDate(digest.digest_date)}
            </Link>
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {digest.content_markdown.substring(0, 150)}...
            </p>
            <p className="text-xs text-gray-400">
              Created {formatDate(digest.created_at)}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


