"use client";

import { useState, useRef, useEffect } from "react";
import { UserButton } from "@clerk/nextjs";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatMessages } from "@/components/chat/ChatMessages";
import { CitationsPanel } from "@/components/chat/CitationsPanel";
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
  // DAO enrichment
  finalVerdict?: string;
  finalConfidence?: number;
  explanation?: {
    issue: string;
    rule: string;
    application: string;
    conclusion: string;
  };
  nextSteps?: string[];
  daoDetails?: any;
  verifierStatus?: string;
  verifierNotes?: string;
  audit?: any;
  agentOutputs?: Array<{
    agent: string;
    verdict: string;
    reasoning_summary: string;
    detailed_reasoning: string;
    sources: string[];
    confidence: number;
    current_weight: number;
    weighted_score?: number;
  }>;
}

export type StructuredCitation = { type: string; reference: string };

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [citations, setCitations] = useState<StructuredCitation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
      // Fetch only the LLM structured response and derive citations from it
      const llmResponse = await fetchLLMResponse(content, caseType, jurisdiction);

      if (llmResponse?.citations) {
        setCitations(llmResponse.citations);
      }

      if (llmResponse) {
        const isFirstResponse = messages.length === 0;

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: isFirstResponse ? 'dao-verdict' : 'assistant',
          content: llmResponse.content,
          timestamp: new Date(),
          agents: isFirstResponse ? llmResponse.agents : undefined,
          explainability: isFirstResponse ? llmResponse.explainability : undefined,
          finalVerdict: llmResponse.final_verdict,
          finalConfidence: llmResponse.final_confidence,
          explanation: llmResponse.explanation,
          nextSteps: llmResponse.next_steps,
          daoDetails: llmResponse.dao_details,
          verifierStatus: llmResponse.verifier_status,
          verifierNotes: llmResponse.verifier_notes,
          audit: llmResponse.audit,
          agentOutputs: llmResponse.agent_outputs,
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
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

  const fetchLLMResponse = async (
    content: string,
    caseType: string,
    jurisdiction: string
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
        }),
      });

      if (!response.ok) throw new Error('Failed to fetch LLM response');

      const data = await response.json();

      // If backend returns structured DAO payload, compose content/explainability for UI
      if (data && data.final_verdict) {
        const composedContent = `Verdict: ${data.final_verdict.replaceAll('_', ' ')} (confidence ${(data.final_confidence * 100).toFixed(1)}%).\n\n${data.explanation?.conclusion ?? ''}`.trim();
        const composedExplainability = `The DAO ensemble aggregated agent votes using confidence × weight. Winning verdict '${data.final_verdict}' achieved ${(data.final_confidence * 100).toFixed(1)}% confidence.`;
        return {
          content: composedContent,
          agents: [
            'BlackLetterStatuteAgent',
            'PrecedentMiner',
            'LimitationProcedureChecker',
            "DevilsAdvocate",
            'DraftingAgent',
            'EthicsAgent',
            'AggregatorAgent',
          ],
          explainability: composedExplainability,
          ...data,
        };
      }

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
