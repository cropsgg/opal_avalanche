"use client";

import { useState, useRef, useEffect } from "react";
import { UserButton } from "@clerk/nextjs";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatMessages } from "@/components/chat/ChatMessages";
import { CitationsPanel } from "@/components/chat/CitationsPanel";
<<<<<<< HEAD
=======
import { apiClient } from "@/lib/api";
>>>>>>> 1a29fd168724437961359413bad99020075647b4
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
<<<<<<< HEAD
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

=======
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

>>>>>>> 1a29fd168724437961359413bad99020075647b4
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
<<<<<<< HEAD
=======
    if (!matterId) {
      console.error('Matter ID not available');
      return;
    }

>>>>>>> 1a29fd168724437961359413bad99020075647b4
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
<<<<<<< HEAD
      // Fetch only the LLM structured response and derive citations from it
      const llmResponse = await fetchLLMResponse(content, caseType, jurisdiction);

      if (llmResponse?.citations) {
        setCitations(llmResponse.citations);
      }

      if (llmResponse) {
=======
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
>>>>>>> 1a29fd168724437961359413bad99020075647b4
        const isFirstResponse = messages.length === 0;

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: isFirstResponse ? 'dao-verdict' : 'assistant',
          content: llmResponse.content,
          timestamp: new Date(),
          agents: isFirstResponse ? llmResponse.agents : undefined,
          explainability: isFirstResponse ? llmResponse.explainability : undefined,
<<<<<<< HEAD
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

=======
          runId: llmResponse.runId,
        };

        // Store the run ID for follow-up messages
        if (llmResponse.runId) {
          setCurrentRunId(llmResponse.runId);
        }

>>>>>>> 1a29fd168724437961359413bad99020075647b4
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
<<<<<<< HEAD
=======
      // Add error message
>>>>>>> 1a29fd168724437961359413bad99020075647b4
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

<<<<<<< HEAD
  const fetchLLMResponse = async (
    content: string,
    caseType: string,
    jurisdiction: string
=======
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
>>>>>>> 1a29fd168724437961359413bad99020075647b4
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
<<<<<<< HEAD
=======
          matterId,
          runId,
>>>>>>> 1a29fd168724437961359413bad99020075647b4
        }),
      });

      if (!response.ok) throw new Error('Failed to fetch LLM response');

      const data = await response.json();
<<<<<<< HEAD

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

=======
>>>>>>> 1a29fd168724437961359413bad99020075647b4
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
