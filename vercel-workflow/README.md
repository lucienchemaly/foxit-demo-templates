# Foxit CRM-to-eSign pipeline as a Vercel Workflow

A durable Vercel Workflow that generates a contract with the Foxit Document
Generation API, sends it for signature with the Foxit eSign API, waits on a
hook for the eSign completion webhook, then downloads the executed PDF.

Companion to the batch5 article3 tutorial.

## Run it

```bash
npm install
cp .env.example .env.local   # fill in your Foxit Developer + eSign keys
npm run dev
```

Trigger the pipeline:

```bash
curl -X POST http://localhost:3000/api/trigger \
  -H "Content-Type: application/json" \
  -d '{"clientName":"Acme Robotics","dealValue":48500,"contractDate":"2026-07-03","lineItems":[{"description":"Annual license","amount":"$48,500.00"}]}'
```

Register `<your-url>/api/foxit-webhook` as the eSign webhook (subscribe
`folder_executed`) so the signed event resumes the workflow. Inspect runs with
`npx workflow web`, or deploy with `vercel deploy --prod` and watch them in the
Vercel dashboard under Observability > Workflows.

## Files

- `workflows/contract.ts` — the `'use workflow'` function plus the three
  `'use step'` functions (generate, send, archive).
- `workflows/hooks.ts` — the `defineHook` the workflow waits on.
- `app/api/trigger/route.ts` — starts a run with `start()`.
- `app/api/foxit-webhook/route.ts` — resumes the hook on `folder_executed`.
- `next.config.ts` — wraps the config with `withWorkflow`.
