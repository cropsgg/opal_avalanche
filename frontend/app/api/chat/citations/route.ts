import { NextRequest, NextResponse } from "next/server";
import { apiClient } from "@/lib/api";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, caseType, jurisdiction, matterId } = body;

    if (!matterId) {
      return NextResponse.json(
        { error: "Matter ID is required" },
        { status: 400 }
      );
    }

    // Send chat message to FastAPI backend
    const response = await apiClient.sendChatMessage({
      matter_id: matterId,
      message: query,
      case_type: caseType,
      jurisdiction_region: jurisdiction,
    });

    if (response.error) {
      return NextResponse.json(
        { error: response.error },
        { status: response.status }
      );
    }

    // Extract citations from the backend response
    const citations = response.data?.citations || [];
    
    return NextResponse.json({
      citations: citations.map((citation: any) => ({
        id: citation.authority_id,
        title: citation.title || citation.cite,
        source: citation.court,
        excerpt: citation.neutral_cite || citation.reporter_cite || '',
        relevanceScore: 0.85, // Default score since not provided
        url: `#citation-${citation.authority_id}`,
        cite: citation.cite,
        para_ids: citation.para_ids
      })),
      query,
      caseType,
      jurisdiction,
      runId: response.data?.run_id
    });

  } catch (error) {
    console.error("Error in citations API:", error);
    return NextResponse.json(
      { error: "Failed to fetch citations" },
      { status: 500 }
    );
  }
}
