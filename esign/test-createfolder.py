"""
End-to-end test: upload sample-text-tags.pdf to the Foxit eSign createfolder
API in base64 mode, request an embedded signing session, and print the session
URL. Uses sendNow:false so the folder stays out of signers' inboxes.

Run:
    export CLIENT_ID=...        # eSign API Key
    export CLIENT_SECRET=...    # eSign API Secret
    python3 test-createfolder.py
"""
import base64
import os

import requests

HOST = "https://na1.foxitesign.foxit.com"
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
SIGNER_EMAIL = os.environ.get("SIGNER_EMAIL", "alex@example.com")


def get_token():
    resp = requests.post(
        f"{HOST}/api/oauth2/access_token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "read-write",
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def main():
    token = get_token()
    with open("sample-text-tags.pdf", "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()

    body = {
        "folderName": "Sample Text Tags Test",
        "sendNow": False,
        "inputType": "base64",
        "base64FileString": [b64],
        "fileNames": ["sample-text-tags.pdf"],
        "createEmbeddedSigningSession": True,
        "embeddedSignersEmailIds": [SIGNER_EMAIL],
        "signSuccessUrl": "https://app.example.com/contracts/signed",
        "signDeclineUrl": "https://app.example.com/contracts/declined",
        "parties": [
            {
                "firstName": "Alex",
                "lastName": "Rivera",
                "emailId": SIGNER_EMAIL,
                "permission": "FILL_FIELDS_AND_SIGN",
                "sequence": 1,
            }
        ],
    }

    resp = requests.post(
        f"{HOST}/api/folders/createfolder",
        headers={"Authorization": f"Bearer {token}"},
        json=body,
    )
    data = resp.json()
    print("result:", data.get("result"))
    print("folderId:", data.get("folder", {}).get("folderId"))
    sessions = data.get("embeddedSigningSessions") or []
    for s in sessions:
        print("session URL:", s["embeddedSessionURL"])


if __name__ == "__main__":
    main()
