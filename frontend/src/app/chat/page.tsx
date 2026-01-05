"use client";

import { Layout } from "@/components/layout/Layout";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { Card, CardContent } from "@/components/ui/card";

export default function ChatPage() {
  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Chat</h1>
          <p className="text-gray-600 mt-2">Ask questions about your stored posts</p>
        </div>

        <Card>
          <CardContent className="p-6">
            <ChatInterface />
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}

