
from pathlib import Path

import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import (
    proportions_ztest,
    confint_proportions_2indep,
)


def load_and_clean():
    """Load the CSV, validate columns, and clean experiment data."""
    path = Path(__file__).parent / "dataset.csv"

    if not path.exists():
        raise FileNotFoundError(
            "dataset.csv was not found."
        )

    df = pd.read_csv(path)

    required = [
        "user_id",
        "timestamp",
        "group",
        "landing_page",
        "converted",
    ]

    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce"
    )
    df["converted"] = pd.to_numeric(
        df["converted"], errors="coerce"
    )

    df = df.dropna(subset=required).copy()

    df = df[
        df["group"].isin(["control", "treatment"])
        & df["landing_page"].isin(["old_page", "new_page"])
        & df["converted"].isin([0, 1])
    ].copy()

    # Keep only rows where the assigned group matches the page.
    valid_assignment = (
        (df["group"] == "control")
        & (df["landing_page"] == "old_page")
    ) | (
        (df["group"] == "treatment")
        & (df["landing_page"] == "new_page")
    )

    df = df[valid_assignment].copy()

    # Classroom policy: retain the first valid observation per user.
    df = df.sort_values("timestamp")
    df = df.drop_duplicates(
        subset="user_id", keep="first"
    )

    if df.empty:
        raise ValueError(
            "No valid observations remain after cleaning."
        )

    if set(df["group"].unique()) != {
        "control", "treatment"
    }:
        raise ValueError(
            "Both control and treatment groups must be present."
        )

    return df


def get_summary(df):
    """Calculate visitors, conversions, and conversion rates."""
    summary = (
        df.groupby("group")
        .agg(
            visitors=("user_id", "nunique"),
            conversions=("converted", "sum"),
            conversion_rate=("converted", "mean"),
        )
        .reindex(["control", "treatment"])
    )

    summary["conversion_pct"] = (
        summary["conversion_rate"] * 100
    )

    summary["non_conversions"] = (
        summary["visitors"] - summary["conversions"]
    )

    return summary


def run_tests(df, summary):
    """Run a two-proportion z-test and a Chi-square test."""
    successes = summary["conversions"].to_numpy(dtype=int)
    sizes = summary["visitors"].to_numpy(dtype=int)

    z_stat, p_value = proportions_ztest(
        count=successes,
        nobs=sizes,
        alternative="two-sided",
    )

    # Rows: experiment groups. Columns: 0 = no, 1 = yes.
    table = pd.crosstab(
        df["group"], df["converted"]
    ).reindex(
        index=["control", "treatment"],
        columns=[0, 1],
        fill_value=0,
    )

    chi2, chi_p, dof, expected = chi2_contingency(table)

    return {
        "z_stat": z_stat,
        "p_value": p_value,
        "chi2": chi2,
        "chi_p": chi_p,
        "dof": dof,
        "expected": expected,
    }


def get_confidence_interval(summary):
    """
    Calculate a 95% confidence interval for:
    treatment conversion rate - control conversion rate.
    """
    treatment_conversions = int(
        summary.loc["treatment", "conversions"]
    )
    treatment_visitors = int(
        summary.loc["treatment", "visitors"]
    )

    control_conversions = int(
        summary.loc["control", "conversions"]
    )
    control_visitors = int(
        summary.loc["control", "visitors"]
    )

    low, high = confint_proportions_2indep(
        count1=treatment_conversions,
        nobs1=treatment_visitors,
        count2=control_conversions,
        nobs2=control_visitors,
        method="newcomb",
        alpha=0.05,
    )

    return low, high


def run_analysis():
    """Run the complete analysis pipeline."""
    df = load_and_clean()
    summary = get_summary(df)
    tests = run_tests(df, summary)

    return df, summary, tests
