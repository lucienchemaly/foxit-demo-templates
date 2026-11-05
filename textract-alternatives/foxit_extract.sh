#!/usr/bin/env bash
# Foxit PDF Services API: upload -> start operation -> poll task -> download.
# Usage: ./foxit_extract.sh structure|ocr-structure|form-data|excel <file.pdf>
# Needs FOXIT_CLIENT_ID and FOXIT_CLIENT_SECRET in the environment, plus curl, jq, unzip.
# Any non-2xx response, missing id or unexpected task status stops the script with the API's
# response on stderr, and polling gives up after MAX_POLLS tries (default 60, 2 s apart).
set -euo pipefail
: "${FOXIT_CLIENT_ID:?set FOXIT_CLIENT_ID to the client ID from your Foxit API console}"
: "${FOXIT_CLIENT_SECRET:?set FOXIT_CLIENT_SECRET to the client secret from your Foxit API console}"
MODE="${1:?usage: $0 structure|ocr-structure|form-data|excel <file.pdf>}"
FILE="${2:?usage: $0 structure|ocr-structure|form-data|excel <file.pdf>}"
MAX_POLLS="${MAX_POLLS:-60}"
HOST="https://na1.fusion.foxit.com/pdf-services/api"
AUTH=(-H "client_id: $FOXIT_CLIENT_ID" -H "client_secret: $FOXIT_CLIENT_SECRET")

fail() { echo "error: $1" >&2; if [ -n "${2:-}" ]; then echo "$2" >&2; fi; exit 1; }

api() {  # api <curl args...> -> prints the response body, stops on a non-2xx status
  local out code
  out=$(curl -sS -w $'\n%{http_code}' "${AUTH[@]}" "$@") || fail "request failed: ${*: -1}"
  code=${out##*$'\n'}; out=${out%$'\n'*}
  [[ $code == 2* ]] || fail "HTTP $code from ${*: -1}" "$out"
  printf '%s' "$out"
}

field() {  # field <json> <key> -> prints the key's value, stops if it is missing or null
  jq -er --arg k "$2" '.[$k] // empty' <<<"$1" 2>/dev/null || fail "no $2 in the API response" "$1"
}

upload() {
  local body
  body=$(api -F "file=@$1" "$HOST/documents/upload") || exit 1
  field "$body" documentId
}

run() {  # run <endpoint> <json body>  -> prints resultDocumentId
  local body task status i
  body=$(api -H "Content-Type: application/json" -d "$2" "$HOST/documents/$1") || exit 1
  task=$(field "$body" taskId) || exit 1
  echo "started $1 (task $task)" >&2
  for ((i = 1; i <= MAX_POLLS; i++)); do
    body=$(api "$HOST/tasks/$task") || exit 1
    status=$(jq -r '.status // empty' <<<"$body")
    case "$status" in
      COMPLETED) field "$body" resultDocumentId; return ;;
      FAILED) fail "task $task failed" "$body" ;;
      PENDING|IN_PROGRESS) sleep 2 ;;
      *) fail "unexpected task status '$status'" "$body" ;;
    esac
  done
  fail "task $task not finished after $MAX_POLLS polls" "$body"
}

download() {
  local code
  code=$(curl -sS -w '%{http_code}' "${AUTH[@]}" -o "$2" "$HOST/documents/$1/download") || fail "download failed"
  [[ $code == 2* ]] || fail "HTTP $code downloading $1" "$(cat "$2")"
}

summarize() {  # trimmed view of StructureInfo.json
  rm -rf out && unzip -o -q "$1" -d out && echo "zip contents: $(unzip -Z1 "$1" | tr '\n' ' ')" >&2
  jq -c '.analyzeResult | .elements //= [] | . as $r | {
        version: $r.version,
        pages: [$r.pages[] | {pageNumber, state, messages}],
        elementTypes: ([$r.elements[].type] | group_by(.) | map({(.[0]): length}) | add),
        textChars: ([$r.elements[] | .content.text // "" | length] | add // 0),
        firstParagraph: ([$r.elements[] | select(.type == "paragraph")][0]
                         | if . == null then null else {text: .content.text, page: .region.page, boundingBox: .region.boundingBox, score} end),
        firstTable: ([$r.elements[] | select(.type == "table")][0]
                     | if . == null then null else {rows: .content.body.rowCount, columns: .content.body.columnCount,
                       scores, image: .originalTableImagePaths[0],
                       firstCells: [(.content.body.cells // [])[0:3][] | {rowIndex, columnIndex, text: .paragraph.content.text}]} end)
      } | to_entries[] | {(.key): .value}' out/StructureInfo.json
}

case "$MODE" in structure|ocr-structure|form-data|excel) ;;
  *) fail "unknown mode '$MODE' (use structure, ocr-structure, form-data or excel)" ;; esac
[ -f "$FILE" ] || fail "file not found: $FILE"
DOC=$(upload "$FILE") || exit 1
echo "uploaded $FILE as $DOC" >&2
case "$MODE" in
  structure)     R=$(run pdf-structural-extract "{\"documentId\":\"$DOC\"}") || exit 1
                 download "$R" result.zip; summarize result.zip ;;
  ocr-structure) O=$(run analyze/pdf-ocr "{\"documentId\":\"$DOC\",\"config\":{\"languages\":[\"en-US\"]}}") || exit 1
                 R=$(run pdf-structural-extract "{\"documentId\":\"$O\"}") || exit 1
                 download "$R" result.zip; summarize result.zip ;;
  form-data)     R=$(run forms/export-pdf-form-data "{\"documentId\":\"$DOC\"}") || exit 1
                 download "$R" form.json; jq . form.json ;;
  excel)         R=$(run convert/pdf-to-excel "{\"documentId\":\"$DOC\"}") || exit 1
                 download "$R" tables.xlsx; echo "saved tables.xlsx" ;;
esac
