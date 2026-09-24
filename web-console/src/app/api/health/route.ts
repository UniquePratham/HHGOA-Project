import { NextResponse } from "next/server";
import { getCases } from "@/lib/casesStore";

export async function GET() {
  return NextResponse.json({
    status: "healthy",
    service: "TigerGraph Agentic Fraud Investigation API (Next.js / Vercel)",
    gateway_mode: "fixture-in-memory",
    active_cases: getCases().length,
    timestamp: new Date().toISOString(),
  });
}
