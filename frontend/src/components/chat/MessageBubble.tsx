"use client";

import { Card, CardContent } from "@/components/ui/card";
import type { Citation } from "@/lib/api/chat";

interface MessageBubbleProps {
  message: string;
  citations?: Citation[];
  isUser?: boolean;
}

export function MessageBubble({ message, citations, isUser }: MessageBubbleProps) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <Card className={`max-w-3xl ${isUser ? "bg-blue-50" : "bg-white"}`}>
        <CardContent className="p-4">
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-900 whitespace-pre-wrap">{message}</p>
            {citations && citations.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-700 mb-2">Sources:</p>
                <ul className="space-y-1">
                  {citations.map((citation) => (
                    <li key={citation.index} className="text-xs">
                      <a
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700"
                      >
                        [{citation.index}] {citation.text_preview}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


