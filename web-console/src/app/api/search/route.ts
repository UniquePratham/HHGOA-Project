import { NextRequest, NextResponse } from "next/server";
import { searchCases } from "@/lib/casesStore";

export async function GET(req: NextRequest) {
  const searchParams = req.nextUrl.searchParams;
  const q = searchParams.get("q") || "";

  if (!q.trim()) {
    return NextResponse.json({ query: "", total_matches: 0, cases: [] });
  }

  const backendUrl = process.env.BACKEND_URL;
  if (backendUrl) {
    try {
      const res = await fetch(`${backendUrl}/api/search?q=${encodeURIComponent(q)}`, {
        next: { revalidate: 0 },
      });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch (e) {
      // Fall through to bundled search
    }
  }

  const results = searchCases(q);
  return NextResponse.json(results);
}
