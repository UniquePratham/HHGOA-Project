import { NextResponse } from "next/server";
import { getCases } from "@/lib/casesStore";

export async function GET() {
  const backendUrl = process.env.BACKEND_URL;
  if (backendUrl) {
    try {
      const res = await fetch(`${backendUrl}/api/cases`, { next: { revalidate: 0 } });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch (e) {
      // Fall through to bundled data
    }
  }

  const cases = getCases();
  return NextResponse.json(cases);
}
