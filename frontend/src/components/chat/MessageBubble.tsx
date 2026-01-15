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
            <div className="text-gray-900 whitespace-pre-wrap">{message}</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
