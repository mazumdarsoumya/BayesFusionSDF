#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 [--raw_root PATH]"
  echo
  echo "This repo does NOT redistribute CO3D."
  echo "Please download CO3D from its official source and place it under raw_root."
}

RAW_ROOT="data/co3d/raw"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --raw_root) RAW_ROOT="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

echo "[INFO] CO3D must be obtained from its official source (manual acceptance may be required)."
echo "[INFO] After downloading, place files under:"
echo "       ${RAW_ROOT}"
echo
echo "[CHECK] Raw root exists?"
if [[ -d "${RAW_ROOT}" ]]; then
  echo "  OK: ${RAW_ROOT}"
else
  echo "  MISSING: ${RAW_ROOT}"
  echo "  Create it and put your downloaded CO3D data there."
fi
