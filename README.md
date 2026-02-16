# MAcc Core Most Beneficial Ranking Workflow

This repository runs a deterministic data workflow to rank **MAcc CORE courses** using only the survey columns that match **Most Beneficial** preferences.

## What the workflow does

- Reads `data/Grad Program Exit Survey Data.xlsx`
- Detects columns whose headers include `MAcc`, `CORE`, and `Most Beneficial` (case-insensitive)
- Calculates average rank by course and response count
- Produces:
  - `outputs/core_course_ranking.csv`
  - `outputs/rank_order.png`

Ranking metric: **average rank per course (lower is better)**.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/rank_core_most_beneficial.py
```

## GitHub Actions

The workflow in `.github/workflows/run_pipeline.yml` runs on every push (and manually via `workflow_dispatch`) and uploads the `outputs/` folder as an artifact named `outputs`.
