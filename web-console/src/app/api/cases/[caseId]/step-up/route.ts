import { NextRequest, NextResponse } from "next/server";
import { updateCaseStepUp } from "@/lib/casesStore";

export async function POST(
  req: NextRequest,
  { params }: { params: { caseId: string } }
) {
  const { caseId } = params;
  const backendUrl = process.env.BACKEND_URL;
  const body = await req.json();

  if (backendUrl) {
    try {
      const res = await fetch(`${backendUrl}/api/cases/${caseId}/step-up`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch (e) {
      // Fall through to in-memory update
    }
  }

  const updated = updateCaseStepUp(
    caseId,
    body.response_status || "CONFIRMED_FRAUD",
    body.notes
  );

  if (!updated) {
    return NextResponse.json({ detail: `Case ${caseId} not found` }, { status: 404 });
  }

  return NextResponse.json(updated);
}
