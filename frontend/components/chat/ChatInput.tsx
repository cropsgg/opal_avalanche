"use client";

<<<<<<< HEAD
import { useState } from "react";
=======
import { useState, useEffect } from "react";
>>>>>>> 1a29fd168724437961359413bad99020075647b4
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Send, Loader2 } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (content: string, caseType: string, jurisdiction: string) => void;
  isLoading: boolean;
}

<<<<<<< HEAD
const CASE_TYPES = [
=======
// Fallback case types in case API is unavailable
const FALLBACK_CASE_TYPES = [
>>>>>>> 1a29fd168724437961359413bad99020075647b4
  "Criminal Law",
  "Civil Rights",
  "Contract Law",
  "Personal Injury",
  "Family Law",
  "Employment Law",
  "Real Estate",
  "Immigration",
  "Bankruptcy",
  "Intellectual Property",
  "Tax Law",
  "Environmental Law",
];

<<<<<<< HEAD
=======
const FALLBACK_JURISDICTIONS = [
  "Federal",
  "California",
  "New York",
  "Texas",
  "Florida",
  "Illinois",
  "Pennsylvania",
  "Ohio",
  "Georgia",
  "North Carolina",
  "Michigan",
  "New Jersey",
];

>>>>>>> 1a29fd168724437961359413bad99020075647b4
export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [caseType, setCaseType] = useState("");
  const [jurisdiction, setJurisdiction] = useState("");
  const [prompt, setPrompt] = useState("");
<<<<<<< HEAD
=======
  const [caseTypes, setCaseTypes] = useState<string[]>(FALLBACK_CASE_TYPES);
  const [jurisdictions, setJurisdictions] = useState<string[]>(FALLBACK_JURISDICTIONS);
  const [loadingOptions, setLoadingOptions] = useState(true);

  useEffect(() => {
    const loadOptions = async () => {
      try {
        const [caseTypesResponse, jurisdictionsResponse] = await Promise.all([
          fetch('/api/case-types'),
          fetch('/api/jurisdictions')
        ]);

        if (caseTypesResponse.ok) {
          const caseTypesData = await caseTypesResponse.json();
          setCaseTypes(caseTypesData);
        }

        if (jurisdictionsResponse.ok) {
          const jurisdictionsData = await jurisdictionsResponse.json();
          setJurisdictions(jurisdictionsData);
        }
      } catch (error) {
        console.error('Failed to load options:', error);
        // Keep fallback data
      } finally {
        setLoadingOptions(false);
      }
    };

    loadOptions();
  }, []);
>>>>>>> 1a29fd168724437961359413bad99020075647b4

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!prompt.trim() || !caseType || !jurisdiction) return;

    onSendMessage(prompt.trim(), caseType, jurisdiction);
    setPrompt("");
  };

  const isFormValid = prompt.trim() && caseType && jurisdiction;

  return (
    <div className="space-y-4">
      {/* First row: Case Type and Jurisdiction */}
      <div className="flex space-x-4">
        <div className="w-1/2">
          <Select value={caseType} onValueChange={setCaseType}>
            <SelectTrigger className="bg-white border-gray-300 text-black">
              <SelectValue placeholder="Select case type" />
            </SelectTrigger>
            <SelectContent className="bg-white border-gray-300">
<<<<<<< HEAD
              {CASE_TYPES.map((type) => (
=======
              {caseTypes.map((type) => (
>>>>>>> 1a29fd168724437961359413bad99020075647b4
                <SelectItem
                  key={type}
                  value={type}
                  className="text-black hover:bg-gray-100"
                >
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="w-1/2">
<<<<<<< HEAD
          <Input
            placeholder="Jurisdiction (e.g., New York, NY)"
            value={jurisdiction}
            onChange={(e) => setJurisdiction(e.target.value)}
            className="bg-white border-gray-300 text-black placeholder:text-gray-500"
          />
=======
          <Select value={jurisdiction} onValueChange={setJurisdiction}>
            <SelectTrigger className="bg-white border-gray-300 text-black">
              <SelectValue placeholder="Select jurisdiction" />
            </SelectTrigger>
            <SelectContent className="bg-white border-gray-300">
              {jurisdictions.map((j) => (
                <SelectItem
                  key={j}
                  value={j}
                  className="text-black hover:bg-gray-100"
                >
                  {j}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
>>>>>>> 1a29fd168724437961359413bad99020075647b4
        </div>
      </div>

      {/* Second row: Prompt input */}
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <Textarea
          placeholder="Enter your legal question or case details..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="flex-1 min-h-[60px] max-h-[120px] bg-white border-gray-300 text-black placeholder:text-gray-500 resize-none"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              if (isFormValid && !isLoading) {
                handleSubmit(e);
              }
            }
          }}
        />

        <Button
          type="submit"
          disabled={!isFormValid || isLoading}
          className="self-end bg-black text-white hover:bg-gray-800 disabled:bg-gray-300"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </Button>
      </form>
    </div>
  );
}
