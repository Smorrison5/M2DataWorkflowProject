from __future__ import annotations

from pathlib import Path
import re

import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = Path("data/Grad Program Exit Survey Data.xlsx")
OUTPUT_DIR = Path("outputs")
CSV_OUTPUT = OUTPUT_DIR / "core_course_ranking.csv"
FIG_OUTPUT = OUTPUT_DIR / "rank_order.png"


def normalize_header(text: str) -> str:
    """Lowercase and collapse whitespace to simplify matching."""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def is_core_most_beneficial_column(header: str) -> bool:
    normalized = normalize_header(header)
    return (
        "macc" in normalized
        and "core" in normalized
        and "most beneficial" in normalized
    )


def extract_course_name(header: str) -> str:
    """Best-effort extraction of course label from survey column text."""
    cleaned = re.sub(r"\s+", " ", str(header)).strip()

    split = re.split(r"most\s+beneficial", cleaned, flags=re.IGNORECASE)
    if len(split) > 1:
        suffix = split[-1].strip(" :-|>\t")
        if suffix:
            return suffix

    parts = re.split(r"\s[-|:]\s", cleaned)
    if len(parts) > 1:
        return parts[-1].strip()

    return cleaned


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Expected dataset at '{DATA_PATH}'. "
            "Ensure the Excel file is committed to the repository at this path."
        )

    df = pd.read_excel(DATA_PATH)

    core_cols = [col for col in df.columns if is_core_most_beneficial_column(col)]
    if not core_cols:
        raise ValueError(
            "No matching columns found for MAcc CORE + Most Beneficial. "
            "Searched headers case-insensitively for all terms: 'MAcc', 'CORE', and 'Most Beneficial'."
        )

    tidy = df[core_cols].melt(var_name="course_header", value_name="rank_value")
    tidy["course"] = tidy["course_header"].map(extract_course_name)
    tidy["course"] = tidy["course"].str.replace(r"\s*-\s*rank\s*$", "", regex=True, flags=re.IGNORECASE).str.strip()
    tidy["rank_value"] = pd.to_numeric(tidy["rank_value"], errors="coerce")
    tidy = tidy.dropna(subset=["rank_value"])

    ranking = (
        tidy.groupby("course", as_index=False)
        .agg(avg_rank=("rank_value", "mean"), n_responses=("rank_value", "size"))
        .sort_values(["avg_rank", "n_responses", "course"], ascending=[True, False, True])
    )
    ranking["avg_rank"] = ranking["avg_rank"].round(3)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ranking.to_csv(CSV_OUTPUT, index=False)

    fig_height = max(4, 0.6 * len(ranking) + 1)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    ax.barh(ranking["course"], ranking["avg_rank"], color="#2E86AB")
    ax.invert_yaxis()
    ax.set_xlabel("Average Rank (Lower = More Beneficial)")
    ax.set_ylabel("Course")
    ax.set_title("MAcc Core Courses — Most Beneficial Ranking")
    ax.grid(axis="x", alpha=0.25)

    for i, value in enumerate(ranking["avg_rank"]):
        ax.text(value, i, f" {value:.2f}", va="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(FIG_OUTPUT, dpi=200)
    plt.close(fig)

    print(f"Columns found: {len(core_cols)}")
    print(f"Rows processed: {len(df)}")
    print(f"CSV output: {CSV_OUTPUT}")
    print(f"Figure output: {FIG_OUTPUT}")


if __name__ == "__main__":
    main()
