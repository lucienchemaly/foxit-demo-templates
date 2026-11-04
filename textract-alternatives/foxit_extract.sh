#!/usr/bin/env bash
# Foxit PDF Services API: upload -> start operation -> poll task -> download.
# Usage: ./foxit_extract.sh structure|ocr-structure|form-data|excel <file.pdf>
# Needs FOXIT_CLIENT_ID and FOXIT_CLIENT_SECRET in the environment, plus curl, jq, unzip.
set -euo pipefail
MODE="$1"; FILE="$2"
HOST="https://na1.fusion.foxit.com/pdf-services/api"
AUTH=(-H "client_id: $FOXIT_CLIENT_ID" -H "client_secret: $FOXIT_CLIENT_SECRET")

upload() { curl -s "${AUTH[@]}" -F "file=@$1" "$HOST/documents/upload" | jq -r .documentId; }

run() {  # run <endpoint> <json body>  -> prints resultDocumentId
  local task status
  task=$(curl -s "${AUTH[@]}" -H "Content-Type: application/json" -d "$2" "$HOST/documents/$1" | jq -r .taskId)
  echo "started $1 (task $task)" >&2
  while :; do
    status=$(curl -s "${AUTH[@]}" "$HOST/tasks/$task")
    case $(jq -r .status <<<"$status") in
      COMPLETED) jq -r .resultDocumentId <<<"$status"; return ;;
      FAILED) echo "$status" >&2; exit 1 ;;
      *) sleep 2 ;;
    esac
  done
}

download() { curl -s "${AUTH[@]}" -o "$2" "$HOST/documents/$1/download"; }

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

DOC=$(upload "$FILE"); echo "uploaded $FILE as $DOC" >&2
case "$MODE" in
  structure)     R=$(run pdf-structural-extract "{\"documentId\":\"$DOC\"}"); download "$R" result.zip; summarize result.zip ;;
  ocr-structure) O=$(run analyze/pdf-ocr "{\"documentId\":\"$DOC\",\"config\":{\"languages\":[\"en-US\"]}}")
                 R=$(run pdf-structural-extract "{\"documentId\":\"$O\"}"); download "$R" result.zip; summarize result.zip ;;
  form-data)     R=$(run forms/export-pdf-form-data "{\"documentId\":\"$DOC\"}"); download "$R" form.json; jq . form.json ;;
  excel)         R=$(run convert/pdf-to-excel "{\"documentId\":\"$DOC\"}"); download "$R" tables.xlsx; echo "saved tables.xlsx" ;;
esac
