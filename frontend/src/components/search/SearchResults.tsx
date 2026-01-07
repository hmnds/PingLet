"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { SearchResult } from "@/lib/api/search";
import { formatDate } from "@/lib/utils/date";
import Link from "next/link";

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
}

export function SearchResults({ results, query }: SearchResultsProps) {
  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No results found for &quot;{query}&quot;</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-600">
        Found {results.length} result{results.length !== 1 ? "s" : ""}
      </p>
      {results.map((result) => (
        <Card key={result.id}>
          <CardContent className="p-6">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="default">Similarity: {(result.similarity * 100).toFixed(1)}%</Badge>
                  <span className="text-xs text-gray-500">{formatDate(result.created_at)}</span>
                </div>
                <p className="text-gray-900 mb-2">{result.text}</p>
                {result.url && (
                  <Link
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    View on X →
                  </Link>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}


