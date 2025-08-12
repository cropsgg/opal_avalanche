"use client";

import { Message } from "@/app/chat/page";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

import { useState, Fragment } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
}

// Hardcoded OPAL Agents map with names and roles
const AGENTS_META = [
  {
    key: "BlackLetterStatuteAgent",
    displayName: "Niyā (निया)",
    role: "Black-Letter Statute Agent",
    subtitle: "Reads bare Acts & maps sections to facts.",
    label: "N",
  },
  {
    key: "PrecedentMiner",
    displayName: "Nyas (न्यास)",
    role: "Precedent Miner",
    subtitle: "Finds controlling/persuasive judgments.",
    label: "Ny",
  },
  {
    key: "LimitationProcedureChecker",
    displayName: "Kāl (काल)",
    role: "Limitation / Procedure Checker",
    subtitle: "Computes deadlines & procedural limits.",
    label: "K",
  },
  {
    key: "RiskStrategyBalancer",
    displayName: "Yoj (योज)",
    role: "Risk / Strategy Balancer",
    subtitle: "Evaluates pros/cons, strategic angles.",
    label: "Y",
  },
  {
    key: "DevilsAdvocate",
    displayName: "Viro (विरोध)",
    role: "Devil's Advocate",
    subtitle: "Argues against your position to stress-test it.",
    label: "V",
  },
  {
    key: "EthicsComplianceSentinel",
    displayName: "Shuc (शुच)",
    role: "Ethics / Compliance Sentinel",
    subtitle: "Flags professional conduct violations.",
    label: "S",
  },
  {
    key: "DraftingAgent",
    displayName: "Lekh (लेख)",
    role: "Drafting Agent",
    subtitle: "Generates first-cut legal drafts.",
    label: "L",
  },
] as const;

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
          {message.type === "user" && <UserMessage message={message} />}

          {message.type === "assistant" && (
            <AssistantMessage message={message} />
          )}

          {message.type === "dao-verdict" && (
            <DAOVerdictMessage message={message} />
          )}
        </div>
      ))}

      {isLoading && (
        <div className="flex items-center space-x-2 text-gray-500">
          <Loader2 className="w-4 h-4 animate-spin" />

          <span>Opal is thinking...</span>
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
                  <span>
                    <strong>Case Type:</strong> {message.caseType}
                  </span>
                  <span>
                    <strong>Jurisdiction:</strong> {message.jurisdiction}
                  </span>
                </div>
              )}

              <p className="text-black whitespace-pre-line">
                {message.content}
              </p>
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
            <p className="text-black whitespace-pre-line">{message.content}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DAOVerdictMessage({ message }: { message: Message }) {
  const outputs = message.agentOutputs || [];
  const displayAgents = AGENTS_META.map((meta) => {
    const found = outputs.find((o) => o.agent === meta.key);
    return { meta, output: found };
  });

  return (
    <div className="flex justify-start">
      <div className="max-w-4xl w-full">
        <Card className="bg-white border-gray-200 shadow-lg">
          <CardContent className="p-6 space-y-4">
            {/* Agent Avatars (clickable) */}
            <div className="flex flex-wrap gap-3 justify-center">
              {displayAgents.map(({ meta, output }) => (
                <AgentPill key={meta.key} meta={meta} output={output} />
              ))}
            </div>

            {/* Final DAO Verdict */}

            <div className="text-center">
              <h3 className="text-xl font-medium text-black">
                Final DAO Verdict
              </h3>
              {message.finalVerdict && (
                <p className="text-sm text-gray-600 mt-1">
                  Verdict:{" "}
                  <span className="font-medium text-black">
                    {message.finalVerdict.replaceAll("_", " ")}
                  </span>
                  {typeof message.finalConfidence === "number" && (
                    <>
                      {" "}
                      · Confidence: {(message.finalConfidence * 100).toFixed(1)}
                      %
                    </>
                  )}
                </p>
              )}
            </div>

            {/* Structured Explanation */}
            {message.explanation && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Section title="Issue" body={message.explanation.issue} />
                <Section title="Rule" body={message.explanation.rule} />
                <Section
                  title="Application"
                  body={message.explanation.application}
                />
                <Section
                  title="Conclusion"
                  body={message.explanation.conclusion}
                />
              </div>
            )}

            {/* Explainability summary */}
            {message.explainability && (
              <div className="border-t border-gray-200 pt-4">
                <h4 className="font-medium text-black mb-1">Explainability</h4>
                <p className="text-gray-700 whitespace-pre-line">
                  {message.explainability}
                </p>
              </div>
            )}

            {/* Next steps */}
            {message.nextSteps && message.nextSteps.length > 0 && (
              <div className="border-t border-gray-200 pt-4">
                <h4 className="font-medium text-black mb-2">Next Steps</h4>
                <ol className="list-decimal pl-5 space-y-1 text-gray-800">
                  {message.nextSteps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function AgentPill({
  meta,
  output,
}: {
  meta: (typeof AGENTS_META)[number];
  output?: NonNullable<Message["agentOutputs"]>[number];
}) {
  const verdict = output?.verdict;
  const weighted =
    typeof output?.weighted_score === "number"
      ? output!.weighted_score
      : output
      ? output.confidence * output.current_weight
      : undefined;
  const ring =
    verdict === "proceed_with_suit"
      ? "ring-green-600"
      : verdict === "do_not_proceed"
      ? "ring-red-600"
      : "ring-gray-400";
  const badgeColor =
    verdict === "proceed_with_suit"
      ? "bg-green-600"
      : verdict === "do_not_proceed"
      ? "bg-red-600"
      : "bg-gray-500";

  return (
    <Dialog>
      <DialogTrigger asChild>
        <button className="flex items-center gap-3 rounded-full border border-gray-200 py-1.5 pl-1.5 pr-3 bg-white hover:shadow-sm">
          <div className="flex flex-col items-center">
            <Avatar className={cn("w-9 h-9 ring-2", ring)}>
              <AvatarFallback className="bg-white text-black border border-gray-300">
                {meta.label}
              </AvatarFallback>
            </Avatar>
            <div
              className={cn(
                "mt-1 text-[10px] text-white px-1.5 py-0.5 rounded",
                badgeColor
              )}
            >
              {typeof weighted === "number" ? weighted.toFixed(3) : "—"}
            </div>
          </div>
          <div className="text-left">
            <div className="text-xs font-semibold text-black leading-tight">
              {meta.displayName}
            </div>
            <div className="text-[11px] text-gray-600 leading-tight">
              {meta.role}
            </div>
          </div>
        </button>
      </DialogTrigger>
      <DialogContent className="bg-white text-black border border-gray-200 max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {meta.displayName} • {meta.role}
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            {meta.subtitle}
          </DialogDescription>
        </DialogHeader>
        {output ? (
          <div className="space-y-3">
            <div className="text-sm">
              <span className="font-medium">Verdict:</span>{" "}
              {output.verdict.replaceAll("_", " ")}
            </div>
            <div className="text-sm">
              <span className="font-medium">Confidence:</span>{" "}
              {(output.confidence * 100).toFixed(1)}%
            </div>
            <div className="text-sm">
              <span className="font-medium">Weight:</span>{" "}
              {output.current_weight}
            </div>
            {typeof output.weighted_score === "number" && (
              <div className="text-sm">
                <span className="font-medium">Weighted score:</span>{" "}
                {output.weighted_score.toFixed(3)}
              </div>
            )}
            {output.reasoning_summary && (
              <div>
                <h5 className="font-medium mb-1">Reasoning summary</h5>
                <p className="text-sm text-gray-800 whitespace-pre-line">
                  {output.reasoning_summary}
                </p>
              </div>
            )}
            {output.detailed_reasoning && (
              <div>
                <h5 className="font-medium mb-1">Detailed reasoning</h5>
                <p className="text-sm text-gray-800 whitespace-pre-line">
                  {output.detailed_reasoning}
                </p>
              </div>
            )}
            {output.sources?.length ? (
              <div>
                <h5 className="font-medium mb-1">Sources</h5>
                <ul className="list-disc pl-5 text-sm text-gray-800">
                  {output.sources.map((s) => (
                    <li key={s}>{s}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : (
          <div className="text-sm text-gray-700">
            No vote recorded for this agent in this run.
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

function Section({ title, body }: { title: string; body: string }) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded p-3">
      <div className="text-sm font-medium text-black mb-1">{title}</div>
      <div className="text-sm text-gray-800 whitespace-pre-line">{body}</div>
    </div>
  );
}
