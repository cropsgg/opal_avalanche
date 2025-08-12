import { NextRequest, NextResponse } from "next/server";
<<<<<<< HEAD
=======
import { apiClient } from "@/lib/api";
>>>>>>> 1a29fd168724437961359413bad99020075647b4

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
<<<<<<< HEAD
    const { query, caseType, jurisdiction } = body;

    // Mock citations data for now - replace with your actual API logic
    const mockCitations = [
      {
        id: "1",
        title: "Smith v. Johnson (2023)",
        source: "Supreme Court Reporter",
        excerpt: "The court held that in matters involving contract interpretation, the plain language of the agreement shall govern unless ambiguity exists that requires extrinsic evidence.",
        relevanceScore: 0.92,
        url: "https://example.com/case/smith-v-johnson"
      },
      {
        id: "2",
        title: "Federal Rules of Civil Procedure Rule 12(b)(6)",
        source: "Federal Rules",
        excerpt: "A party may move to dismiss for failure to state a claim upon which relief can be granted. The motion must be made before pleading if a responsive pleading is allowed.",
        relevanceScore: 0.78,
        url: "https://example.com/rules/frcp-12b6"
      },
      {
        id: "3",
        title: "Legal Standards for Contract Formation",
        source: "Restatement (Second) of Contracts",
        excerpt: "A contract is formed when there is an offer, acceptance, and consideration. The parties must have mutual assent to the essential terms.",
        relevanceScore: 0.65,
        url: "https://example.com/restatement/contracts"
      }
    ];

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    return NextResponse.json({
      citations: mockCitations,
      query,
      caseType,
      jurisdiction
=======
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
>>>>>>> 1a29fd168724437961359413bad99020075647b4
    });

  } catch (error) {
    console.error("Error in citations API:", error);
    return NextResponse.json(
      { error: "Failed to fetch citations" },
      { status: 500 }
    );
  }
}
