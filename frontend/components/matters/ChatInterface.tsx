'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Send, Bot, User, FileText, Scale } from 'lucide-react';

interface ChatInterfaceProps {
  matterId: string;
  disabled?: boolean;
  onEvidenceSelect: (evidence: any) => void;
}

const mockMessages = [
  {
    id: '1',
    type: 'user',
    content: 'What are the key precedents for breach of contract damages in commercial disputes?',
    timestamp: '2 hours ago'
  },
  {
    id: '2',
    type: 'assistant',
    content: 'Based on the analysis of your documents and legal precedents, here are the key cases for commercial contract breach damages:\n\n1. **Hadley v Baxendale (1854)** - Established the rule for consequential damages\n2. **Victoria Laundry v Newman Industries (1949)** - Extended the Hadley rule\n3. **Koufos v Czarnikow (1969)** - The Heron II case on remoteness',
    timestamp: '2 hours ago',
    evidence: [
      {
        case: 'Hadley v Baxendale',
        citation: '(1854) 9 Exch 341',
        relevance: 'High',
        paragraphs: ['23', '24', '25']
      },
      {
        case: 'Victoria Laundry v Newman',
        citation: '[1949] 2 KB 528',
        relevance: 'High',
        paragraphs: ['15', '16']
      }
    ]
  }
];

export function ChatInterface({ matterId, disabled, onEvidenceSelect }: ChatInterfaceProps) {
  const [messages, setMessages] = useState(mockMessages);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState('general');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: input,
      timestamp: 'Just now'
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant' as const,
        content: 'I\'m analyzing your query and searching through legal precedents. This would normally connect to the OPAL API for real-time legal research.',
        timestamp: 'Just now',
        evidence: []
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 2000);
  };

  const handleEvidenceClick = (evidence: any) => {
    onEvidenceSelect(evidence);
  };

  return (
    <Card className="bg-cream-100 border-stone-200 h-[600px] flex flex-col">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-display text-brown-900 flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Legal Research Chat
          </CardTitle>
          <Select value={mode} onValueChange={setMode} disabled={disabled}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="general">General</SelectItem>
              <SelectItem value="precedent">Precedent</SelectItem>
              <SelectItem value="limitation">Limitation</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex gap-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' ? 'bg-brown-700 text-cream-100' : 'bg-gold-500 text-brown-900'
                }`}>
                  {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>
                
                <div className={`rounded-lg p-4 ${
                  message.type === 'user' 
                    ? 'bg-brown-700 text-cream-100' 
                    : 'bg-white border border-stone-200'
                }`}>
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {message.content}
                  </div>
                  
                  {message.evidence && message.evidence.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <div className="text-xs text-brown-500 font-medium">Citations & Evidence:</div>
                      {message.evidence.map((evidence: any, index: number) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          onClick={() => handleEvidenceClick(evidence)}
                          className="text-xs mr-2 mb-2"
                        >
                          <Scale className="h-3 w-3 mr-1" />
                          {evidence.case}
                        </Button>
                      ))}
                    </div>
                  )}
                  
                  <div className="text-xs opacity-70 mt-2">
                    {message.timestamp}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-gold-500 text-brown-900 flex items-center justify-center">
                <Bot className="h-4 w-4" />
              </div>
              <div className="bg-white border border-stone-200 rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-brown-700"></div>
                  <span className="text-sm text-brown-500">Researching legal precedents...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t pt-4">
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={disabled ? 'Please wait for document processing to complete...' : 'Ask about legal precedents, case law, or document analysis...'}
              disabled={disabled || isLoading}
              className="min-h-[80px] resize-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <Button 
              onClick={handleSend} 
              disabled={disabled || isLoading || !input.trim()}
              className="bg-brown-700 hover:bg-brown-500 text-cream-100"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}