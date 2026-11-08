#!/bin/bash
TEMA="$*"
agentcore invoke --runtime agent --payload "{\"prompt\": \"Escribe un guion de TikTok sobre $TEMA\"}" 2>&1 \
  | grep -o '"text": "\([^"\\]\|\\.\)*"' \
  | sed 's/^"text": "//; s/"$//' \
  | tr -d '\n' \
  | sed 's/<thinking>[^<]*<\/thinking>//g; s/\\n/\n/g; s/\\"/"/g'
echo
