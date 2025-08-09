'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Send, Bot, User, FileText, Scale, Loader2, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import type { ChatMessage, ChatMode, Citation, EvidenceItem } from '@/types';

interface ChatInterfaceProps {
  matterId: string;
  disabled?: boolean;
  onEvidenceSelect: (evidence: EvidenceItem | null) => void;
  onRunComplete?: (runId: string) => void;
}

export function ChatInterface({ matterId, disabled, onEvidenceSelect, onRunComplete }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<ChatMode>('general');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat history when component mounts
  useEffect(() => {
    loadChatHistory();
  }, [matterId]);

  const loadChatHistory = async () => {
    // For now, we'll start with an empty chat
    // In a full implementation, we'd load previous chat history from the backend
    setMessages([]);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading || disabled) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
      mode
    };

    const currentInput = input.trim();
    setInput('');
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.sendChatMessage({
        matterId,
        message: currentInput,
        mode,
        filters: {} // TODO: Add filter support
      });

      if (response.error) {
        setError(response.error);
        toast({
          title: 'Error',
          description: response.error,
          variant: 'destructive'
        });
        
        // Remove loading message on error
        setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
        return;
      }

      if (response.data) {
        const aiMessage: ChatMessage = {
          id: response.data.run_id,
          type: 'assistant',
          content: response.data.answer,
          timestamp: new Date().toISOString(),
          evidence: response.data.citations.map(citation => ({
            case: citation.title || citation.cite || 'Legal Authority',
            citation: citation.cite,
            relevance: 'High' as const, // TODO: Determine relevance from confidence
            paragraphs: citation.para_ids.map(id => id.toString()),
            authority_id: citation.authority_id.toString(),
            court: citation.court,
            snippet: '' // TODO: Add snippet extraction
          })),
          run_id: response.data.run_id,
          confidence: response.data.confidence
        };

        setMessages(prev => [...prev, aiMessage]);

        // If there are citations, auto-select the first one
        if (aiMessage.evidence && aiMessage.evidence.length > 0) {
          onEvidenceSelect(aiMessage.evidence[0]);
        }
        
        // Show success notification
        toast({
          title: 'Analysis Complete',
          description: `Found ${aiMessage.evidence?.length || 0} relevant authorities with ${Math.round((aiMessage.confidence || 0) * 100)}% confidence.`,
        });

        // Notify parent component of new run completion
        if (onRunComplete && response.data.run_id) {
          onRunComplete(response.data.run_id);
        }
      }
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMsg);
      toast({
        title: 'Error',
        description: 'Failed to send message. Please try again.',
        variant: 'destructive'
      });
      
      // Remove user message on error
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvidenceClick = (evidence: EvidenceItem) => {
    onEvidenceSelect(evidence);
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
      return date.toLocaleDateString();
    } catch {
      return 'Recently';
    }
  };

  const getModeLabel = (mode: ChatMode) => {
    switch (mode) {
      case 'general': return 'General Research';
      case 'precedent': return 'Precedent Analysis';
      case 'limitation': return 'Limitation Check';
      case 'draft': return 'Document Drafting';
      default: return 'Legal Research';
    }
  };

  const getModeDescription = (mode: ChatMode) => {
    switch (mode) {
      case 'general': return 'General legal research and analysis';
      case 'precedent': return 'Find and analyze relevant case precedents';
      case 'limitation': return 'Check limitation periods and deadlines';
      case 'draft': return 'Get help with document drafting';
      default: return 'Choose a research mode';
    }
  };

  return (
    <div className="space-y-4">
      {/* Mode Selection Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-blue-900">{getModeLabel(mode)}</h3>
              <p className="text-sm text-blue-700">{getModeDescription(mode)}</p>
            </div>
            <Select value={mode} onValueChange={(value: ChatMode) => setMode(value)} disabled={disabled || isLoading}>
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
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Chat Interface */}
      <Card className="bg-cream-100 border-stone-200 h-[600px] flex flex-col">
        <CardHeader className="pb-4">
          <CardTitle className="text-xl font-display text-brown-900 flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Legal Research Chat
          </CardTitle>
        </CardHeader>

      <CardContent className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.length === 0 && !isLoading && (
            <div className="flex items-center justify-center h-full text-center">
              <div className="space-y-4">
                <Bot className="h-16 w-16 text-brown-400 mx-auto" />
                <div>
                  <h3 className="text-lg font-medium text-brown-900 mb-2">
                    Start Your Legal Research
                  </h3>
                  <p className="text-brown-500 text-sm max-w-md">
                    Ask questions about your case, search for precedents, check limitation periods, 
                    or get help with document drafting. OPAL&apos;s AI will search through legal authorities 
                    and provide detailed analysis with citations.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 justify-center">
                  <Badge variant="outline" className="text-xs">Contract disputes</Badge>
                  <Badge variant="outline" className="text-xs">Precedent analysis</Badge>
                  <Badge variant="outline" className="text-xs">Limitation periods</Badge>
                  <Badge variant="outline" className="text-xs">Legal drafting</Badge>
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex gap-3 max-w-[85%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === 'user' ? 'bg-brown-700 text-cream-100' : 'bg-gold-500 text-brown-900'
                }`}>
                  {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>
                
                <div className={`rounded-lg p-4 ${
                  message.type === 'user' 
                    ? 'bg-brown-700 text-cream-100' 
                    : 'bg-white border border-stone-200 shadow-sm'
                }`}>
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {message.content}
                  </div>
                  
                  {/* Confidence indicator for AI messages */}
                  {message.type === 'assistant' && message.confidence && (
                    <div className="mt-2 flex items-center gap-2">
                      <span className="text-xs text-brown-500">Confidence:</span>
                      <div className="flex-1 bg-stone-200 rounded-full h-1.5">
                        <div 
                          className="bg-green-500 h-1.5 rounded-full" 
                          style={{ width: `${message.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-brown-600 font-medium">
                        {Math.round(message.confidence * 100)}%
                      </span>
                    </div>
                  )}
                  
                  {message.evidence && message.evidence.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <div className="text-xs text-brown-500 font-medium flex items-center gap-1">
                        <Scale className="h-3 w-3" />
                        Citations & Evidence ({message.evidence.length}):
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {message.evidence.map((evidence, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            size="sm"
                            onClick={() => handleEvidenceClick(evidence)}
                            className="text-xs border-brown-300 hover:bg-brown-50"
                          >
                            <FileText className="h-3 w-3 mr-1" />
                            {evidence.case}
                            <Badge variant="secondary" className="ml-2 text-xs">
                              {evidence.court}
                            </Badge>
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-opacity-20">
                    <div className="text-xs opacity-70">
                      {formatTimestamp(message.timestamp)}
                    </div>
                    {message.mode && (
                      <Badge variant="outline" className="text-xs">
                        {getModeLabel(message.mode)}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-gold-500 text-brown-900 flex items-center justify-center">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
              <div className="bg-white border border-stone-200 rounded-lg p-4 shadow-sm">
                <div className="flex items-center gap-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-brown-600 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-brown-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-brown-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-brown-500">
                    {mode === 'precedent' ? 'Analyzing precedents...' :
                     mode === 'limitation' ? 'Checking limitation periods...' :
                     mode === 'draft' ? 'Preparing draft suggestions...' :
                     'Researching legal authorities...'}
                  </span>
                </div>
                <div className="text-xs text-brown-400 mt-1">
                  This may take a few seconds while our AI searches through legal databases
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t pt-4">
          <div className="flex gap-2">
            <div className="flex-1">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={
                  disabled 
                    ? 'Please wait for document processing to complete...' 
                    : mode === 'precedent'
                    ? 'Ask about relevant case precedents, binding authorities, or conflicting decisions...'
                    : mode === 'limitation'
                    ? 'Check limitation periods, computation rules, or time-barred claims...'
                    : mode === 'draft'
                    ? 'Get help with document drafting, clauses, or legal language...'
                    : 'Ask about legal precedents, case law, statutes, or get analysis help...'
                }
                disabled={disabled || isLoading}
                className="min-h-[80px] resize-none border-stone-300 focus:border-brown-500"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
              />
              <div className="flex items-center justify-between mt-2 text-xs text-brown-400">
                <span>Press Enter to send, Shift+Enter for new line</span>
                <span>{input.length}/2000</span>
              </div>
            </div>
            <Button 
              onClick={handleSend} 
              disabled={disabled || isLoading || !input.trim() || input.length > 2000}
              className="bg-brown-700 hover:bg-brown-600 text-cream-100 self-end"
              size="lg"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
    </div>
  );
}