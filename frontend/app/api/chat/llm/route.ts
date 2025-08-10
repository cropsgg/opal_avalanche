import { NextRequest, NextResponse } from "next/server";
import { apiClient } from "@/lib/api";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, caseType, jurisdiction, matterId, runId } = body;

    let response;
    
    if (runId) {
      // This is a follow-up message
      response = await apiClient.sendChatFollowup({
        matter_id: matterId,
        run_id: runId,
        message: query,
      });
    } else {
      // This is the initial chat message
      if (!matterId) {
        return NextResponse.json(
          { error: "Matter ID is required" },
          { status: 400 }
        );
      }

      response = await apiClient.sendChatMessage({
        matter_id: matterId,
        message: query,
        case_type: caseType,
        jurisdiction_region: jurisdiction,
      });
    }

    if (response.error) {
      return NextResponse.json(
        { error: response.error },
        { status: response.status }
      );
    }

    // Format response for frontend
    const formattedResponse = {
      content: response.data?.answer || 'No response received',
      agents: [
        "Ethics Agent",
        "Precedent Agent",
        "Devil's Advocate Agent",
        "Drafting Agent",
        "Limitation Agent",
        "Aggregator Agent",
        "Base Agent"
      ],
      explainability: `This verdict was reached through a comprehensive analysis involving seven specialized AI agents. Each agent contributed unique expertise to ensure a well-rounded, thorough analysis of your ${caseType || 'legal'} matter in ${jurisdiction || 'the specified jurisdiction'}.`,
      runId: response.data?.run_id,
      confidence: response.data?.confidence,
      evidenceMerkleRoot: (response.data as any)?.evidence_merkle_root
    };

    return NextResponse.json(formattedResponse);

  } catch (error) {
    console.error("Error in LLM API:", error);
    return NextResponse.json(
      { error: "Failed to get LLM response" },
      { status: 500 }
    );
  }
}
