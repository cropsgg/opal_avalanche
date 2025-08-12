import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    // Ignore request body and return hardcoded payload for demo
    const agent_outputs = [
      {
        agent: "BlackLetterStatuteAgent",
        verdict: "proceed_with_suit",
        reasoning_summary:
          "Statutory text of Section 17(1)(b) makes clear that where a defendant conceals title or right by fraud, limitation begins on discovery. Client discovered fraud in July 2021; therefore limitation runs from July 2021 and a suit filed in 2022 is within three years.",
        detailed_reasoning:
          "Step 1: Identify cause of action and discovery date. Step 2: Apply Section 17(1)(b) → limitation tolls until discovery. Step 3: Compute 3-year period from discovery (July 2021 → July 2024). Conclusion: filing in 2022 falls within this period, subject to proof of concealment.",
        sources: [
          "Limitation Act, 1963 — Section 17(1)(b)",
          "Limitation Act, 1963 — Section 3",
        ],
        confidence: 0.92,
        current_weight: 1.0,
        weighted_score: 0.92 * 1.0,
      },
      {
        agent: "PrecedentMiner",
        verdict: "proceed_with_suit",
        reasoning_summary:
          "Recent Supreme Court precedents (e.g., SLP No. 12658/2025) reaffirm that fraud delays the running of limitation until discovery. Where fraud has been concealed and discovery occurs later, courts have allowed suits filed within the statutory period post-discovery.",
        detailed_reasoning:
          "Cites CIVIL APPEAL No. 1796/2024 for the principle that written acknowledgements can reset limitation where present, and SLP No. 12658/2025 for fraud-concealment tolling. Emphasizes gathering contemporaneous documents evidencing discovery and concealment (title search, emails).",
        sources: [
          "CIVIL APPEAL No. 1796/2024",
          "SPECIAL LEAVE PETITION (CIVIL) No. 12658/2025",
        ],
        confidence: 0.88,
        current_weight: 0.95,
        weighted_score: 0.88 * 0.95,
      },
      {
        agent: "LimitationProcedureChecker",
        verdict: "proceed_with_suit",
        reasoning_summary:
          "Numeric computation: discovery July 2021 + 3-year limitation → expiry July 2024. Filing in 2022 is within the computed window. Check for acknowledgements (Section 18) and any possible earlier discoverability.",
        detailed_reasoning:
          "Compute: discovery = July 2021. Add 3 years = July 2024. Verify no written acknowledgement post-dating discovery that would further modify dates. Validate documentary evidence proving exact discovery date to rebut earlier discoverability arguments.",
        sources: [
          "Limitation Act, 1963 — Section 3",
          "Limitation Act, 1963 — Section 18",
        ],
        confidence: 0.90,
        current_weight: 1.0,
        weighted_score: 0.9 * 1.0,
      },
      {
        agent: "DevilsAdvocate",
        verdict: "do_not_proceed",
        reasoning_summary:
          "Risk scenario: Defendant may contend that the plaintiff had constructive or actual knowledge of the defect earlier than July 2021 (e.g., through public records or earlier communications), or that concealment is not established. If court accepts earlier discoverability, suit may be time-barred.",
        detailed_reasoning:
          "Cites CIVIL APPEAL No. 6843/2025 which underscores strict application of limitation. Recommends preparing evidence to rebut constructive knowledge: timeline of due diligence, title search dates, absence of public notice, and the specific manner of concealment.",
        sources: [
          "CIVIL APPEAL No. 6843/2025",
          "CIVIL APPEAL No. 4718/2025",
        ],
        confidence: 0.78,
        current_weight: 1.0,
        weighted_score: 0.78 * 1.0,
      },
    ];

    const payload = {
      run_id: "3e804c6b-f05b-4a47-b837-cd1bcc567fd3",
      final_verdict: "proceed_with_suit",
      final_confidence: 0.773,
      explanation: {
        issue:
          "Whether the property dispute suit is time-barred under the Limitation Act, 1963 given that the alleged fraud was discovered in July 2021 and the suit was filed in 2022.",
        rule:
          "Section 3 of the Limitation Act prescribes the period of limitation for suits; Section 17(1)(b) tolls the running of limitation where the plaintiff's right is concealed by fraud until the fraud is discovered. Section 18 permits resetting the period when a written acknowledgement exists. Supreme Court precedents reinforce these principles (e.g., SLP(C) No. 12658/2025 on fraud-concealment; CIVIL APPEAL No. 1796/2024 on acknowledgements; CIVIL APPEAL No. 6843/2025 on strictness of limitation).",
        application:
          "1) Discovery date: contemporaneous evidence (email July 20, 2021; independent title search July 25, 2021) shows when the client learned of the defect. 2) Tolling under Section 17(1)(b): If the seller actively concealed the defect (seller withheld title information or forged document elements such that a reasonable title search would not have revealed it), limitation begins on discovery (July 2021). 3) Computation: three years from discovery → July 2021 + 3 years = July 2024. Numeric check: 0.92*1.0 + 0.88*0.95 + 0.90*1.0 = 0.92 + 0.836 + 0.90 = 2.656 (total weighted score for 'proceed_with_suit'). Opposing score: 0.78 (Devil's Advocate). Aggregate total = 2.656 + 0.78 = 3.436; final confidence = 2.656 / 3.436 ≈ 0.773. 4) Precedential support: SLP(C) No. 12658/2025 directly supports tolling on discovery; CIVIL APPEAL No. 1796/2024 explains when acknowledgements can change computation. 5) Risks: CIVIL APPEAL No. 6843/2025 warns courts enforce limitation strictly — the defendant can argue earlier discoverability or absence of concealment. Under CIVIL APPEAL No. 4718/2025, courts may adjudicate discoverability as a mixed question at trial; this suggests factual preparation is crucial.",
        conclusion:
          "On the facts asserted (fraud discovered July 2021; filing in 2022), the claim appears to be within the limitation period and actionable, provided the plaintiff can prove concealment and the actual date of discovery. The DAO (weighted agent ensemble) therefore recommends proceeding with the suit, subject to collecting and preserving documentary evidence to rebut discoverability arguments.",
      },
      next_steps: [
        "Prepare & file plaint in the Delhi High Court (if not already filed). The safe computation on these facts is: limitation runs from discovery (July 2021); a suit filed in 2022 is within three years post-discovery.",
        "Assemble documentary evidence proving date of discovery and concealment: (a) email dated July 20, 2021 describing the discovery, (b) independent title search dated July 25, 2021, (c) correspondence seeking clarification from seller (Aug 2021), (d) any forensic analysis of the sale deed (handwriting/signature analysis), and (e) copies of the original sale deed and registry entries.",
        "Draft pleadings to emphasise fraud & concealment: include a separate averment with timeline of concealment, annex contemporaneous communications as proof of discovery, cite Section 17(1)(b) Limitation Act and SLP(C) No. 12658/2025, and attach the title search report as an annexure.",
        "Prepare to rebut defendant’s discoverability arguments: obtain affidavits from (i) client confirming date and circumstances of discovery, (ii) the independent search provider detailing limitations of public records at time of purchase, (iii) legal counsel who advised at the time (if any).",
        "Consider seeking an early interim remedy (e.g., injunction) if there is a risk of further alienation, and include reliefs for injunction, declaration, and recovery as per facts.",
        "If there is any written acknowledgment from the defendant post-discovery, collect and flag it — CIVIL APPEAL No. 1796/2024 shows such evidence can materially affect limitation computation.",
        "Notarize the run/audit bundle (Merkle root) on Avalanche Fuji for an immutable record of cited paras and retrieval set before filing; include notarization tx link in the plea bundle as provenance for authorities relied upon.",
        "If the suit was not filed within the three-year window or there are borderline timing issues, prepare a condonation application demonstrating sufficient cause and emphasize fraudulent concealment as a statutory tolling ground (cite SLP(C) No. 12658/2025).",
      ],
      citations: [
        { type: 'statute', reference: 'Limitation Act, 1963 — Section 17(1)(b)' },
        { type: 'statute', reference: 'Limitation Act, 1963 — Section 3' },
        { type: 'statute', reference: 'Limitation Act, 1963 — Section 18' },
        { type: 'case', reference: 'SPECIAL LEAVE PETITION (CIVIL) No. 12658/2025 — (Supreme Court) (fraud-concealment tolling)' },
        { type: 'case', reference: 'CIVIL APPEAL No. 1796/2024 — (Supreme Court) (acknowledgement resetting limitation)' },
        { type: 'case', reference: 'CIVIL APPEAL No. 6843/2025 — (Supreme Court) (strict application of limitation)' },
        { type: 'case', reference: 'CIVIL APPEAL No. 4718/2025 — (Supreme Court) (limitation as mixed question of law & fact)' },
      ],
      dao_details: {
        agent_votes: agent_outputs.map((a) => ({
          agent: a.agent,
          verdict: a.verdict,
          confidence: a.confidence,
          weight: a.current_weight,
          weighted_score: a.weighted_score,
        })),
        weighted_scores_summary: {
          proceed_with_suit: 2.656,
          do_not_proceed: 0.78,
        },
        final_confidence_explanation:
          "final_confidence = proceed_with_suit_total / (all_verdict_totals) = 2.656 / 3.436 ≈ 0.773",
      },
      verifier_status: 'pass',
      verifier_notes:
        'All statutory references and cited precedents were cross-checked against retrieval set; no unsupported citations were found. Limitation arithmetic validated. Jurisdiction (Delhi High Court) is appropriate for the property location.',
      audit: {
        run_id: '3e804c6b-f05b-4a47-b837-cd1bcc567fd3',
        evidence_merkle_root:
          '0x4b8f9d2a3f9c1e8b6a7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9',
        timestamp_utc: '2025-08-10T03:58:00Z',
      },
    } as const;

    const content = `Verdict: ${payload.final_verdict.replaceAll('_', ' ')} (confidence ${(payload.final_confidence * 100).toFixed(1)}%).\n\n${payload.explanation.conclusion}`;
    const explainability = `The DAO ensemble aggregated agent votes using confidence × weight. Winning verdict '${payload.final_verdict}' achieved ${(payload.final_confidence * 100).toFixed(1)}% confidence.`;

    // Simulate slight delay
    await new Promise((r) => setTimeout(r, 500));

    return NextResponse.json({
      ...payload,
      content,
      explainability,
      agents: agent_outputs.map((a) => a.agent),
      agent_outputs,
    });
  } catch (error) {
    console.error("Error in LLM API:", error);
    return NextResponse.json(
      { error: "Failed to get LLM response" },
      { status: 500 }
    );
  }
}
