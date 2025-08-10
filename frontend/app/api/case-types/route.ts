import { NextResponse } from "next/server";
import { apiClient } from "@/lib/api";

export async function GET() {
  try {
    const response = await apiClient.getCaseTypes();
    
    if (response.error) {
      // Fallback to static options if backend is unavailable
      return NextResponse.json([
        "Contract Law",
        "Employment Law", 
        "Personal Injury",
        "Real Estate",
        "Family Law",
        "Criminal Law",
        "Corporate Law",
        "Intellectual Property",
        "Immigration Law",
        "Tax Law"
      ]);
    }
    
    return NextResponse.json(response.data || []);
  } catch (error) {
    console.error("Error fetching case types:", error);
    
    // Return fallback data
    return NextResponse.json([
      "Contract Law",
      "Employment Law", 
      "Personal Injury",
      "Real Estate",
      "Family Law",
      "Criminal Law",
      "Corporate Law",
      "Intellectual Property",
      "Immigration Law",
      "Tax Law"
    ]);
  }
}
