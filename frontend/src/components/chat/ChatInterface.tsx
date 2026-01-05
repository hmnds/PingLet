"use client";

import { useState, useRef, useEffect } from "react";
import { MessageBubble } from "./MessageBubble";
import { chatApi } from "@/lib/api/chat";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Send } from "lucide-react";

interface Message {
  question: string;
  answer: string;
  citations?: any[];
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || isLoading) return;

    const userQuestion = question.trim();
    setQuestion("");
    setError(null);

    // Add user message
    setMessages((prev) => [...prev, { question: userQuestion, answer: "" }]);

    try {
      setIsLoading(true);
      const response = await chatApi.chat(userQuestion);
      
      // Update last message with answer
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          question: userQuestion,
          answer: response.answer,
          citations: response.citations,
        };
        return newMessages;
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to get answer");
      setMessages((prev) => prev.slice(0, -1)); // Remove the user message on error
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px]">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-12">
            Ask a question to get started
          </div>
        )}
        {messages.map((message, index) => (
          <div key={index} className="space-y-4">
            <MessageBubble message={message.question} isUser />
            <MessageBubble message={message.answer} citations={message.citations} />
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <Card className="bg-gray-50">
              <CardContent className="p-4">
                <p className="text-gray-600">Thinking...</p>
              </CardContent>
            </Card>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="mb-4 p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          className="flex-1 h-10 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        />
        <Button type="submit" disabled={isLoading || !question.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}

