"""
Minimal Foxit eSign webhook receiver with HMAC-SHA-256 signature verification.

Foxit eSign signs every webhook POST with an HMAC-SHA-256 digest of the RAW
request body, computed with your Webhook Secret, base64-encoded, and delivered
as a `signature` query string parameter on the callback URL:

    https://your-app.example.com/webhook?signature=XXXXXXXX

This receiver recomputes the same HMAC over the unparsed raw body and compares
it with hmac.compare_digest. Verify against the raw bytes, never the re-serialized
JSON, since any whitespace or key-ordering change breaks the comparison.

Run:
    export WEBHOOK_SECRET=...      # the Webhook Secret from the eSign API settings page
    python3 webhook_receiver.py   # listens on 0.0.0.0:8000

Then expose it publicly (e.g. `ngrok http 8000`) and register the public
https URL under the eSign portal's API settings -> Webhooks section.
"""
import base64
import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]


def verify_webhook_signature(raw_body: bytes, signature_param: str) -> bool:
    computed = base64.b64encode(
        hmac.new(WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(computed, signature_param)


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        raw_body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        sig = parse_qs(urlparse(self.path).query).get("signature", [""])[0]
        valid = verify_webhook_signature(raw_body, sig)

        event = "(unparsed)"
        status = "(unknown)"
        try:
            payload = json.loads(raw_body)
            event = payload.get("event_name", event)
            status = payload.get("data", {}).get("folder", {}).get("folderStatus", status)
        except (ValueError, AttributeError):
            pass

        print(f"[webhook] event={event} folderStatus={status} signature_valid={valid}")

        if not valid:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"invalid signature")
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass  # silence default access logging; we print our own line


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"Foxit eSign webhook receiver listening on :{port}")
    HTTPServer(("0.0.0.0", port), WebhookHandler).serve_forever()
