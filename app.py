import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from analysis import (
    run_analysis,
    get_confidence_interval,
)

# Set professional light-theme aesthetics for Seaborn/Matplotlib
sns.set_theme(style="whitegrid", palette="muted")

st.set_page_config(
    page_title="E-Commerce A/B Testing Dashboard",
    page_icon="🛒",
    layout="wide",
)

# App Header
st.title("🛒 E-Commerce A/B Testing Analytics")
st.markdown(
    "Comprehensive performance evaluation comparing the **Control (Old Page)** "
    "versus the **Treatment (New Page)** using live customer conversion data."
)

# Load Data Safely
try:
    df, summary, tests = run_analysis()
    ci_low, ci_high = get_confidence_interval(summary)

except Exception as error:
    st.error(f"Unable to execute analysis pipeline: {error}")
    st.stop()

# Dataset Inspection Expander
with st.expander("🔍 Inspect Cleaned Dataset & Diagnostics"):
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.metric("Dataset Shape", f"{df.shape[0]:,} rows × {df.shape[1]} cols")
    with col_b:
        st.write("Missing Values per Column:")
        st.dataframe(df.isna().sum(), use_container_width=True)
    
    st.write("Data Preview (First 10 Rows):")
    st.dataframe(df.head(10), use_container_width=True)

# Calculate Key Metrics
control_rate = summary.loc["control", "conversion_rate"]
treatment_rate = summary.loc["treatment", "conversion_rate"]
absolute_lift = treatment_rate - control_rate

relative_lift = (
    (absolute_lift / control_rate) * 100
    if control_rate != 0
    else None
)

# KPI Overview Section
st.subheader("📊 Experiment Overview & Core KPIs")

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Control Conversion Rate",
    value=f"{control_rate:.2%}",
)

col2.metric(
    label="Treatment Conversion Rate",
    value=f"{treatment_rate:.2%}",
    delta=f"{absolute_lift * 100:+.2f} percentage pts",
)

col3.metric(
    label="Relative Conversion Lift",
    value=f"{relative_lift:+.2f}%" if relative_lift is not None else "N/A",
)

st.markdown("---")

st.subheader("📋 Group Conversion Summary")

display_summary = summary[
    [
        "visitors",
        "conversions",
        "non_conversions",
        "conversion_pct",
    ]
].rename(
    columns={
        "visitors": "Visitors",
        "conversions": "Conversions",
        "non_conversions": "Non-conversions",
        "conversion_pct": "Conversion Rate (%)",
    }
)

st.dataframe(
    display_summary.round(3),
    use_container_width=True,
)

# Visualizations Section
st.subheader("📈 Visual Analytics & Distributions")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**1. Traffic Distribution by Group**")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=summary.reset_index(),
        x="group",
        y="visitors",
        hue="group",
        legend=False,
        ax=ax,
    )
    ax.set_xlabel("Experiment Group")
    ax.set_ylabel("Unique Visitors")
    ax.set_title("Visitors in Each Group")
    st.pyplot(fig)
    plt.close(fig)

with chart_col2:
    st.markdown("**2. Outcome Breakdown**")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(
        data=df,
        x="group",
        hue="converted",
        order=["control", "treatment"],
        hue_order=[0, 1],
        ax=ax,
    )
    ax.set_xlabel("Experiment Group")
    ax.set_ylabel("Number of Users")
    ax.set_title("Converted vs. Not Converted")
    ax.legend(title="Converted", labels=["No", "Yes"])
    st.pyplot(fig)
    plt.close(fig)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown("**3. Conversion Rate Comparison**")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=summary.reset_index(),
        x="group",
        y="conversion_pct",
        hue="group",
        legend=False,
        ax=ax,
    )
    ax.set_xlabel("Experiment Group")
    ax.set_ylabel("Conversion Rate (%)")
    ax.set_title("Old Page vs. New Page")
    st.pyplot(fig)
    plt.close(fig)

with chart_col4:
    st.markdown("**4. Daily Conversion Trends**")
    daily = (
        df.assign(date=df["timestamp"].dt.date)
        .groupby(["date", "group"])["converted"]
        .mean()
        .reset_index(name="conversion_rate")
    )
    daily["conversion_pct"] = daily["conversion_rate"] * 100

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.lineplot(
        data=daily,
        x="date",
        y="conversion_pct",
        hue="group",
        marker="o",
        ax=ax,
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Conversion Rate (%)")
    ax.set_title("Daily Conversion Trends")
    plt.xticks(rotation=45)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.markdown("---")

# Statistical Testing Section
st.subheader("🔬 Statistical Hypothesis Testing")

st.write(
    "* **Null Hypothesis (H₀):** Control and treatment conversion rates are equal."
    "\n* **Alternative Hypothesis (H₁):** Population conversion rates differ."
)

alpha = 0.05
p_value = tests["p_value"]

stat_col1, stat_col2, stat_col3 = st.columns(3)

stat_col1.metric("Z-statistic", f'{tests["z_stat"]:.4f}')
stat_col2.metric("P-value", f"{p_value:.6f}")
stat_col3.metric("Significance Level (α)", f"{alpha:.2f}")

if p_value < alpha:
    st.success(
        "**Reject H₀:** Statistically significant difference detected between the conversion rates."
    )
else:
    st.info(
        "**Fail to Reject H₀:** Insufficient evidence to establish a significant difference."
    )

# Chi-Square Cross-Check Expander
with st.expander("🧪 Chi-Square Test Cross-Check Details"):
    st.write(f"Chi-square statistic: `{tests['chi2']:.4f}`")
    st.write(f"Chi-square p-value: `{tests['chi_p']:.6f}`")
    st.caption(
        "Both the two-proportion z-test and Chi-square test evaluate the same relationship "
        "for this binary outcome setup and should align closely."
    )

# Confidence Interval Section
st.subheader("📏 95% Confidence Interval")

st.write(
    f"* **Estimated Difference (Treatment − Control):** `{absolute_lift * 100:+.2f} percentage points`"
    f"\n* **95% Confidence Interval:** `{ci_low * 100:+.2f} to {ci_high * 100:+.2f} percentage points`"
)

if ci_low > 0:
    st.write("The interval lies entirely above zero, indicating a positive treatment effect.")
elif ci_high < 0:
    st.write("The interval lies entirely below zero, indicating a negative treatment effect.")
else:
    st.write("The interval spans zero, meaning a clear positive or negative effect cannot be confirmed.")

st.markdown("---")

# Business Interpretation Section
st.subheader("💡 Business Interpretation & Recommendations")

if absolute_lift > 0:
    direction = "higher than"
elif absolute_lift < 0:
    direction = "lower than"
else:
    direction = "equal to"

st.write(
    f"The treatment group's observed conversion rate is **{direction}** the control group's rate, "
    f"reflecting an absolute change of **{absolute_lift * 100:+.2f} percentage points**."
)

if p_value < alpha and ci_low > 0:
    st.success(
        "🚀 **Recommendation:** The new page delivers a statistically significant positive lift. "
        "Review implementation costs and operational metrics before rolling out globally."
    )
elif p_value < alpha and ci_high < 0:
    st.warning(
        "⚠️ **Recommendation:** The new page yields a statistically significant negative impact. "
        "Investigate user experience bottlenecks before considering release."
    )
else:
    st.info(
        "🔍 **Recommendation:** No statistically significant difference was established at the 5% level. "
        "Consider running the experiment longer to capture higher statistical power."
    )

st.divider()

st.caption(
    "📊 Dataset: A/B Testing Conversion Rate | "
    "Note: Analysis evaluates conversion rates, not revenue or order value metrics."
)
