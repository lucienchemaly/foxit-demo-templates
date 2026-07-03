import { NextResponse } from "next/server";
import { start } from "workflow/api";
import { contractWorkflow, type Deal } from "@/workflows/contract";

// POST here (from a CRM webhook) to start the durable pipeline.
export async function POST(req: Request) {
  const body = (await req.json().catch(() => ({}))) as Partial<Deal>;
  const deal: Deal = {
    clientName: body.clientName ?? "Acme Robotics",
    dealValue: body.dealValue ?? 48500,
    contractDate: body.contractDate ?? "2026-07-03",
    lineItems: body.lineItems ?? [
      { description: "Platform license (annual)", amount: "$36,000.00" },
    ],
  };
  await start(contractWorkflow, [deal]);
  return NextResponse.json({ started: true });
}
