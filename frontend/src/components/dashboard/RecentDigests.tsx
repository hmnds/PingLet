import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useLatestDigest, useRunDigest } from "@/hooks/useDigests";
import { formatDate } from "@/lib/utils/date";
import { cn } from "@/lib/utils/cn";
import { Play } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export function RecentDigests() {
  const { data: digest, isLoading } = useLatestDigest();
  const runDigest = useRunDigest();
  const [isRunning, setIsRunning] = useState(false);

  const handleRunDigest = async () => {
    try {
      setIsRunning(true);
      await runDigest.mutateAsync(undefined);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Card className="glass-card flex flex-col h-full">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="text-lg font-semibold text-slate-800">Latest Digest</CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRunDigest}
          disabled={isRunning}
          className="rounded-full shadow-sm hover:shadow-md transition-all"
        >
          <Play className={cn("mr-2 h-3 w-3", isRunning && "animate-spin")} />
          {isRunning ? "Generating..." : "Run Now"}
        </Button>
      </CardHeader>
      <CardContent className="flex-1">
        {isLoading ? (
          <div className="flex items-center justify-center h-32 text-slate-400">Loading...</div>
        ) : !digest ? (
          <div className="text-center py-8 text-slate-500 bg-slate-50/50 rounded-xl border border-slate-100">
            <p>No digests generated yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="pb-4 border-b border-slate-100">
              <p className="text-lg font-bold text-slate-800">
                {formatDate(digest.digest_date)}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Generated {formatDate(digest.created_at)}
              </p>
            </div>
            <div className="text-sm text-slate-600 line-clamp-3 leading-relaxed">
              {digest.content_markdown.substring(0, 200)}...
            </div>
            <div className="pt-2">
              <Link
                href={`/digests/${digest.digest_date}`}
                className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors group"
              >
                Read full digest
                <span className="ml-1 group-hover:translate-x-1 transition-transform">→</span>
              </Link>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}


