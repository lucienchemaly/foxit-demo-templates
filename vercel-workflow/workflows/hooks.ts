import { defineHook } from "workflow";

// The payload Foxit eSign POSTs to the webhook when a folder is executed.
export type FoxitCompletion = {
  event_name: string;
  data: { folder: { folderId: number; folderStatus: string } };
};

// A durable hook the workflow waits on. It is resumed server-side from the
// /api/foxit-webhook route by calling signatureHook.resume(token, payload).
export const signatureHook = defineHook<FoxitCompletion>();
