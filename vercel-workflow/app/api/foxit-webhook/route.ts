import { signatureHook } from "@/workflows/hooks";

// Foxit eSign POSTs here on folder_executed. Resuming the hook by the
// folderId token wakes the paused workflow so it can archive the signed PDF.
export async function POST(req: Request) {
  const payload = await req.json();
  const folderId = payload?.data?.folder?.folderId;
  // Resume only on the terminal event, so earlier lifecycle events
  // (viewed, signed, completed) do not consume the single-use hook.
  if (folderId && payload?.event_name === "folder_executed") {
    await signatureHook.resume(String(folderId), payload);
  }
  return new Response("OK");
}
