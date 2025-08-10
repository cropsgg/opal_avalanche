"use client";

import { Message } from "@/app/chat/page";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
}

const AGENT_AVATARS = [
  { name: "Ethics", color: "bg-blue-500" },
  { name: "Precedent", color: "bg-green-500" },
  { name: "Devil", color: "bg-red-500" },
  { name: "Drafting", color: "bg-purple-500" },
  { name: "Limitation", color: "bg-yellow-500" },
  { name: "Aggregator", color: "bg-indigo-500" },
  { name: "Base", color: "bg-gray-500" },
];

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <div className="text-6xl font-light text-black mb-4">Opal</div>
          <p className="text-lg">Ask your legal question to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {messages.map((message) => (
        <div key={message.id} className="space-y-2">
          {message.type === 'user' && (
            <UserMessage message={message} />
          )}

          {message.type === 'assistant' && (
            <AssistantMessage message={message} />
          )}

          {message.type === 'dao-verdict' && (
            <DAOVerdictMessage message={message} />
          )}
        </div>
      ))}

      {isLoading && (
        <div className="flex items-center space-x-2 text-gray-500">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Analyzing your case...</span>
        </div>
      )}
    </div>
  );
}

function UserMessage({ message }: { message: Message }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-3xl">
        <Card className="bg-gray-100 border-gray-200">
          <CardContent className="p-4">
            <div className="space-y-2">
              {message.caseType && message.jurisdiction && (
                <div className="text-sm text-gray-600 flex space-x-4">
                  <span><strong>Case Type:</strong> {message.caseType}</span>
                  <span><strong>Jurisdiction:</strong> {message.jurisdiction}</span>
                </div>
              )}
              <p className="text-black">{message.content}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function AssistantMessage({ message }: { message: Message }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-3xl">
        <Card className="bg-white border-gray-200">
          <CardContent className="p-4">
            <p className="text-black">{message.content}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DAOVerdictMessage({ message }: { message: Message }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-4xl w-full">
        <Card className="bg-white border-gray-200 shadow-lg">
          <CardContent className="p-6">
            {/* Agent Avatars */}
            <div className="flex justify-center space-x-2 mb-4">
              {AGENT_AVATARS.map((agent, index) => (
                <Avatar key={index} className="w-10 h-10">
                  <AvatarFallback className={cn("text-white text-xs", agent.color)}>
                    {agent.name.charAt(0)}
                  </AvatarFallback>
                </Avatar>
              ))}
            </div>

            {/* Final DAO Verdict */}
            <div className="text-center mb-4">
              <h3 className="text-xl font-medium text-black">Final DAO Verdict</h3>
            </div>

            {/* Main Content */}
            <div className="space-y-4">
              <p className="text-black leading-relaxed">{message.content}</p>

              {/* Explainability */}
              {message.explainability && (
                <div className="border-t border-gray-200 pt-4">
                  <div className="space-y-2">
                    <h4 className="font-medium text-black">Explainability:</h4>
                    <p className="text-gray-700 leading-relaxed">
                      {message.explainability}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
