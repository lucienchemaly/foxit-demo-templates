import { signatureHook } from "./hooks";

export type Deal = {
  clientName: string;
  dealValue: number;
  contractDate: string;
  lineItems: { description: string; amount: string }[];
};

const DOCGEN_URL =
  "https://na1.fusion.foxit.com/document-generation/api/GenerateDocumentBase64";
const ESIGN = "https://na1.foxitesign.foxit.com";
const TEMPLATE_URL =
  "https://github.com/lucienchemaly/foxit-demo-templates/raw/main/contract_signing.docx";

// The durable workflow. It survives deploys and crashes and resumes exactly
// where it left off, including across the multi-day signing wait.
export async function contractWorkflow(deal: Deal) {
  "use workflow";

  const pdfBase64 = await generateContract(deal);
  const folderId = await sendForSignature(pdfBase64, deal);

  // Pause until Foxit's folder_executed webhook resumes this hook.
  const completion = await signatureHook.create({ token: String(folderId) });

  const archivedBytes = await archiveSigned(folderId);
  return { folderId, event: completion.event_name, archivedBytes };
}

async function generateContract(deal: Deal) {
  "use step";

  const template = await fetch(TEMPLATE_URL);
  const base64FileString = Buffer.from(
    await template.arrayBuffer(),
  ).toString("base64");

  const res = await fetch(DOCGEN_URL, {
    method: "POST",
    headers: {
      client_id: process.env.FOXIT_DOCGEN_CLIENT_ID!,
      client_secret: process.env.FOXIT_DOCGEN_CLIENT_SECRET!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      base64FileString,
      documentValues: deal,
      outputFormat: "pdf",
    }),
  });
  if (!res.ok) throw new Error(`DocGen failed: ${res.status}`);
  const json = await res.json();
  return json.base64FileString as string;
}

async function esignToken() {
  const res = await fetch(`${ESIGN}/api/oauth2/access_token`, {
    method: "POST",
    body: new URLSearchParams({
      grant_type: "client_credentials",
      client_id: process.env.FOXIT_ESIGN_CLIENT_ID!,
      client_secret: process.env.FOXIT_ESIGN_CLIENT_SECRET!,
      scope: "read-write",
    }),
  });
  const { access_token } = await res.json();
  return access_token as string;
}

async function sendForSignature(pdfBase64: string, deal: Deal) {
  "use step";

  const token = await esignToken();
  const res = await fetch(`${ESIGN}/api/folders/createfolder`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      folderName: `Contract - ${deal.clientName}`,
      inputType: "base64",
      base64FileString: [pdfBase64],
      fileNames: ["contract.pdf"],
      processTextTags: true,
      sendNow: true,
      parties: [
        {
          firstName: "Alex",
          lastName: "Rivera",
          emailId: "alex.rivera@example.com",
          permission: "FILL_FIELDS_AND_SIGN",
          sequence: 1,
          workflowSequence: 1,
        },
      ],
    }),
  });
  const data = await res.json();
  const party = data.folder?.folderRecipientParties?.[0];
  console.log("SIGNER_URL", data.folder.folderId, party?.folderAccessURL);
  return data.folder.folderId as number;
}

async function archiveSigned(folderId: number) {
  "use step";

  const token = await esignToken();
  const res = await fetch(`${ESIGN}/api/folders/download?folderId=${folderId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return (await res.arrayBuffer()).byteLength;
}
