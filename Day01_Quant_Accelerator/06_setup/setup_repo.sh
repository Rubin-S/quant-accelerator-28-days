#!/usr/bin/env bash
# Day 1 setup: one research repo for the whole 28 days. Fedora/Linux.
# Usage: bash setup_repo.sh ~/quant-accelerator
set -euo pipefail
DIR="${1:-$HOME/quant-accelerator}"
mkdir -p "$DIR"/{data/raw,data/clean,notebooks,src,tests,reports,logs}
cd "$DIR"
git init -q 2>/dev/null || true
# uv: fast Python env manager (https://docs.astral.sh/uv/)
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv init --no-workspace --python 3.12 . 2>/dev/null || true
uv add numpy pandas matplotlib scipy statsmodels jupyterlab pytest yfinance
cat > .gitignore <<'G'
.venv/
data/raw/
__pycache__/
*.parquet
.ipynb_checkpoints/
.env
G
cat > README.md <<'R'
# Quant Accelerator (31 Oct - 27 Nov 2026)
One strategy, NSE index ETFs/index, daily bars. Every test logged in logs/trial-log.csv.
R
echo "Done. Next: copy training-log.md + trial-log.csv into $DIR/logs and who_pays_whom.py into $DIR/src, then: cd $DIR && uv run python src/who_pays_whom.py"
git add -A && git commit -qm "Day 1: repo skeleton" || true
