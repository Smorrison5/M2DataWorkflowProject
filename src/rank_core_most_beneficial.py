from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = Path("data/Grad Program Exit Survey Data.xlsx")
OUTPUT_DIR = Path("outputs")
CSV_OUTPUT = OUTPUT_DIR / "core_course_ranking.csv"
FIG_OUTPUT = OUTPUT_DIR / "rank_order.png"


def simplify_course_name(column_name: str) -> str:
    """Extract a clean course label from the original survey column name."""
    cleaned = " ".join(str(column_name).strip().split())
    lowered = cleaned.lower()

    if "most beneficial" in lowered:
        index = lowered.index("most beneficial")
        cleaned = cleaned[:index].rstrip(" -:|/")

    for prefix in ("MAcc CORE", "MAcc Core", "CORE", "Core"):
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].lstrip(" -:|/")
            break

    return cleaned if cleaned else str(column_name)


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Input data file not found: {DATA_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(DATA_PATH)

    matching_columns = [
        col
        for col in df.columns
        if "macc" in str(col).lower()
        and "core" in str(col).lower()
        and "most beneficial" in str(col).lower()
    ]

    if not matching_columns:
        raise ValueError(
            "No matching columns found for pattern: headers containing "
            "'MAcc', 'CORE', and 'Most Beneficial' (case-insensitive)."
        )

    tidy = df[matching_columns].melt(var_name="course", value_name="rank_value")
    tidy["rank_value"] = pd.to_numeric(tidy["rank_value"], errors="coerce")
    tidy = tidy.dropna(subset=["rank_value"]).copy()
    tidy["course"] = tidy["course"].map(simplify_course_name)

    ranking = (
        tidy.groupby("course", as_index=False)
        .agg(avg_rank=("rank_value", "mean"), n_responses=("rank_value", "size"))
        .sort_values(["avg_rank", "n_responses", "course"], ascending=[True, False, True])
        .reset_index(drop=True)
    )
    ranking["avg_rank"] = ranking["avg_rank"].round(2)

    ranking.to_csv(CSV_OUTPUT, index=False)

    fig, ax = plt.subplots(figsize=(10, max(4.5, 0.6 * len(ranking))))
    ax.barh(ranking["course"], ranking["avg_rank"], color="#1f77b4")
    ax.set_xlabel("Average Rank (Lower = More Beneficial)")
    ax.set_ylabel("Course")
    ax.set_title("MAcc Core Courses — Most Beneficial Ranking")
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    max_rank = ranking["avg_rank"].max() if not ranking.empty else 0
    for i, value in enumerate(ranking["avg_rank"]):
        ax.text(value + max_rank * 0.02, i, f"{value:.2f}", va="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(FIG_OUTPUT, dpi=180)
    plt.close(fig)

    print(f"Columns found: {len(matching_columns)}")
    print(f"Rows processed (non-missing ranks): {len(tidy)}")
    print(f"CSV output: {CSV_OUTPUT}")
    print(f"Figure output: {FIG_OUTPUT}")


if __name__ == "__main__":
    main()
