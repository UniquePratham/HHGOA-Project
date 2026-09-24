import { NextRequest, NextResponse } from "next/server";
import { getCaseById } from "@/lib/casesStore";

export async function GET(
  req: NextRequest,
  { params }: { params: { caseId: string } }
) {
  const { caseId } = params;
  const backendUrl = process.env.BACKEND_URL;

  if (backendUrl) {
    try {
      const res = await fetch(`${backendUrl}/api/cases/${caseId}`, { next: { revalidate: 0 } });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch (e) {
      // Fall through to bundled data
    }
  }

  const c = getCaseById(caseId);
  if (!c) {
    return NextResponse.json({ detail: `Case ${caseId} not found` }, { status: 404 });
  }

  return NextResponse.json(c);
}
