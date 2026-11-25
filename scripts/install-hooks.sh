#!/usr/bin/env bash
set -euo pipefail
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
echo "Git hooks installed: pre-commit (lint) and pre-push (tests+coverage)."
