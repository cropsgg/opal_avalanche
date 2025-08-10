"use client";

import { useState, useRef, useEffect } from "react";
import { UserButton } from "@clerk/nextjs";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatMessages } from "@/components/chat/ChatMessages";
import { CitationsPanel } from "@/components/chat/CitationsPanel";
import { apiClient } from "@/lib/api";
import { Inter, Poppins } from "next/font/google";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'dao-verdict';
  content: string;
  timestamp: Date;
  caseType?: string;
  jurisdiction?: string;
  agents?: string[];
  explainability?: string;
  runId?: string;
}

export interface Citation {
  id: string;
  title: string;
  source: string;
  excerpt: string;
  relevanceScore: number;
  url?: string;
  cite?: string;
  para_ids?: number[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [matterId, setMatterId] = useState<string | null>(null);
  const [currentRunId, setCurrentRunId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Create a matter when the component loads
  useEffect(() => {
    const createMatter = async () => {
      try {
        const response = await apiClient.createMatter({
          title: `Chat Session - ${new Date().toLocaleDateString()}`
        });
        
        if (response.data) {
          const id = 'matter_id' in response.data ? response.data.matter_id : response.data.id;
          setMatterId(id);
        }
      } catch (error) {
        console.error('Failed to create matter:', error);
      }
    };
    
    createMatter();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (
    content: string,
    caseType: string,
    jurisdiction: string
  ) => {
    if (!matterId) {
      console.error('Matter ID not available');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
      caseType,
      jurisdiction,
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Determine if this is a follow-up message
      const isFollowUp = currentRunId && messages.length > 0;
      
      // Send two parallel requests - one for citations and one for the LLM response
      const [citationsResponse, llmResponse] = await Promise.all([
        fetchCitations(content, caseType, jurisdiction, matterId, isFollowUp ? currentRunId : undefined),
        fetchLLMResponse(content, caseType, jurisdiction, matterId, isFollowUp ? currentRunId : undefined),
      ]);

      // Update citations
      if (citationsResponse) {
        setCitations(citationsResponse);
      }

      // Add LLM response
      if (llmResponse) {
        // Check if this is the first response (show DAO verdict)
        const isFirstResponse = messages.length === 0;

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: isFirstResponse ? 'dao-verdict' : 'assistant',
          content: llmResponse.content,
          timestamp: new Date(),
          agents: isFirstResponse ? llmResponse.agents : undefined,
          explainability: isFirstResponse ? llmResponse.explainability : undefined,
          runId: llmResponse.runId,
        };

        // Store the run ID for follow-up messages
        if (llmResponse.runId) {
          setCurrentRunId(llmResponse.runId);
        }

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCitations = async (
    content: string,
    caseType: string,
    jurisdiction: string,
    matterId: string,
    runId?: string
  ): Promise<Citation[] | null> => {
    try {
      const response = await fetch('/api/chat/citations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: content,
          caseType,
          jurisdiction,
          matterId,
          runId,
        }),
      });

      if (!response.ok) throw new Error('Failed to fetch citations');

      const data = await response.json();
      return data.citations || [];
    } catch (error) {
      console.error('Error fetching citations:', error);
      return null;
    }
  };

  const fetchLLMResponse = async (
    content: string,
    caseType: string,
    jurisdiction: string,
    matterId: string,
    runId?: string
  ): Promise<any | null> => {
    try {
      const response = await fetch('/api/chat/llm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: content,
          caseType,
          jurisdiction,
          matterId,
          runId,
        }),
      });

      if (!response.ok) throw new Error('Failed to fetch LLM response');

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching LLM response:', error);
      return null;
    }
  };

  return (
    <div className={`${poppins.variable} ${inter.variable} min-h-screen bg-white text-black`}>
      {/* Header */}
      <ChatHeader />

      {/* Main Content */}
      <div className="flex h-[calc(100vh-64px)]">
        {/* Chat Section */}
        <div className="flex-1 flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6">
            <ChatMessages
              messages={messages}
              isLoading={isLoading}
            />
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-6">
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Citations Panel */}
        <div className="w-80 border-l border-gray-200">
          <CitationsPanel citations={citations} />
        </div>
      </div>
    </div>
  );
}
