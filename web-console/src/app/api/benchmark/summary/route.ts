import { NextResponse } from "next/server";
import { getBenchmarkSummary } from "@/lib/casesStore";

export async function GET() {
  const backendUrl = process.env.BACKEND_URL;
  if (backendUrl) {
    try {
      const res = await fetch(`${backendUrl}/api/benchmark/summary`, { next: { revalidate: 0 } });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch (e) {
      // Fall through to bundled summary
    }
  }

  const summary = getBenchmarkSummary();
  return NextResponse.json(summary);
}
