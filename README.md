# MAcc Core Course Ranking Workflow

This repository contains a deterministic data workflow that ranks **MAcc CORE courses** using only the survey's **Most Beneficial** ranking columns.

## What the workflow does
- Reads `data/Grad Program Exit Survey Data.xlsx`
- Detects headers containing `MAcc`, `CORE`, and `Most Beneficial` (case-insensitive)
- Converts ranking values to numeric and ignores blanks/non-numeric entries
- Calculates ranking using average rank per course (**lower average rank = more beneficial**)
- Generates:
  - `outputs/core_course_ranking.csv`
  - `outputs/rank_order.png`

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/rank_core_most_beneficial.py
```

## GitHub Actions
The workflow in `.github/workflows/run_pipeline.yml` runs on:
- `push`
- manual trigger (`workflow_dispatch`)
- merged pull requests (`pull_request` closed events where `merged == true`)

It uploads the `outputs/` directory as an artifact named `outputs`.

## Output location
All generated files appear in the `outputs/` directory.
