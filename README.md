# E-Commerce A/B Testing Analysis

A Python and Streamlit project that compares an old and a new e-commerce landing page using A/B testing. The dashboard explores user conversion behavior, visualizes experiment results and applies statistical tests to assess whether the observed conversion-rate difference is statistically significant.

## Project Objectives

- Compare conversion rates for the control and treatment groups.
- Clean and validate the experiment dataset before analysis.
- Visualize group sizes, conversion outcomes, conversion rates and daily trends.
- Apply a two-proportion z-test and a chi-square test.
- Report a 95% confidence interval for the difference in conversion rates.
- Present the findings in an interactive Streamlit dashboard.

## Dataset

**Dataset:** AB Testing Conversion Rate  
**Source repository:** https://github.com/yangfuchun/AB_Testing_Conversion_Rate

Save the CSV file in the project folder as `dataset.csv`.

The analysis expects these columns:

| Column | Description |
|---|---|
| `user_id` | Identifier for a user |
| `timestamp` | Time associated with the experiment record |
| `group` | Experiment group: `control` or `treatment` |
| `landing_page` | Page shown: `old_page` or `new_page` |
| `converted` | Binary outcome: `1` means converted; `0` means not converted |

This dataset records conversion outcomes. It does **not** contain purchase amounts or revenue, so the project does not estimate revenue, profit or average order value.

## Project Structure

```text
Project_02_Ecommerce_AB_Testing/
├── app.py
├── analysis.py
├── dataset.csv
├── requirements.txt
├── README.md
└── images/
    └── dashboard.png
```

- `app.py` — Streamlit interface, metrics, charts, statistical results and interpretation.
- `analysis.py` — Data loading, cleaning, summary statistics and hypothesis tests.
- `dataset.csv` — Input dataset downloaded from the source repository.
- `requirements.txt` — Python dependencies.
- `images/dashboard.png` — Optional screenshot of the completed dashboard.

## Technologies Used

- Python
- Pandas and NumPy
- Streamlit
- Matplotlib and Seaborn
- SciPy
- Statsmodels

## Setup and Run

### 1. Create and open the project folder

Open a terminal in the project directory.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
```

Or on Windows Command Prompt:

```bat
.venv\\Scripts\\activate.bat
```

### 3. Install dependencies

Ensure `requirements.txt` includes:

```text
pandas
numpy
matplotlib
seaborn
scipy
statsmodels
streamlit
```

Then run:

```bash
python -m pip install -r requirements.txt
```

### 4. Add the dataset

Download the dataset from the source repository and save the CSV file as `dataset.csv` in the same folder as `app.py` and `analysis.py`.

### 5. Launch the dashboard

```bash
python -m streamlit run app.py
```

Streamlit will provide a local URL in the terminal, usually `http://localhost:8501`.

## Analysis Workflow

1. Load the CSV file and check for required columns.
2. Parse timestamps and convert the conversion outcome to a numeric value.
3. Remove records with missing or invalid required values.
4. Keep rows where the group matches the landing page:
   - `control` with `old_page`
   - `treatment` with `new_page`
5. Sort records by timestamp and keep the first valid record for each user.
6. Calculate unique visitors, conversions and conversion rates for both groups.
7. Visualize experiment group sizes, conversion outcomes, conversion-rate comparison and daily conversion trends.
8. Run statistical tests and display the results in the dashboard.

**Data-cleaning note:** Keeping the first valid record per user is a deliberate choice for this project, not a universal rule. A real experiment should confirm its randomization unit, assignment consistency, duplicate-record policy and handling of repeated sessions before analysis.

## Statistical Methods

### Conversion Rate

Conversion rate is calculated as:

`Conversion rate = Number of conversions / Number of visitors`

A conversion rate of `0.08` corresponds to 8%.

### Hypothesis Test

The project uses a two-sided two-proportion z-test.

- **Null hypothesis (H₀):** The population conversion rates are equal.
- **Alternative hypothesis (H₁):** The population conversion rates differ.
- **Significance level:** `α = 0.05`

Interpretation:

- If `p-value < 0.05`, reject H₀; the data provide evidence of a difference between the conversion rates.
- If `p-value >= 0.05`, fail to reject H₀; the data do not provide sufficient evidence of a difference at the 5% level.

A p-value is **not** the probability that the null hypothesis is true. A non-significant result also does not prove that the two pages perform identically.

### Chi-Square Cross-Check

A chi-square test of independence is also applied to the group-by-conversion contingency table. It provides a cross-check for association between experiment group and conversion outcome. Since both tests use the same underlying observations, they are not independent pieces of evidence.

### Confidence Interval

The dashboard reports a 95% confidence interval for:

`Treatment conversion rate − Control conversion rate`

- An interval entirely above zero indicates a positive difference under the chosen method.
- An interval entirely below zero indicates a negative difference.
- An interval that includes zero does not establish a difference at the corresponding two-sided 5% level.

The confidence interval helps communicate the estimated effect and its uncertainty; it does not measure business value directly.

## Dashboard Features

- Preview of the cleaned dataset and missing-value summary
- Control and treatment conversion-rate metrics
- Absolute difference in percentage points and relative lift
- Experiment group-size chart
- Conversion outcome chart
- Conversion-rate comparison chart
- Daily conversion trend chart
- Z-statistic, p-value and significance-level display
- Chi-square test results
- 95% confidence interval and business interpretation

## Limitations

- The dataset measures conversion outcomes, not revenue or profit.
- Statistical significance alone is not enough to justify launching a new page.
- Conclusions depend on sound random assignment, independent observations, adequate sample size and appropriate data cleaning.
- The daily trend chart is descriptive; day-to-day changes should not automatically be treated as statistically meaningful.
- The project is an educational analysis and should not replace a full experiment review for a production business decision.

## Future Improvements

- Add a downloadable cleaned dataset and results report.
- Add filters for date range and experiment group.
- Include a test-selection explanation and assumptions checklist.
- Add automated data-quality checks for assignment mismatches and duplicate users.
- Add a deployment guide for hosting the Streamlit dashboard.

## Learning Outcomes

By completing this project, learners practice data cleaning, exploratory data analysis, conversion-rate calculation, hypothesis testing, confidence intervals, visualization and communicating statistical findings to a business audience.

## Acknowledgements

The dataset is sourced from the [AB_Testing_Conversion_Rate repository](https://github.com/yangfuchun/AB_Testing_Conversion_Rate). Please review the source repository's terms and licence before redistributing the dataset.
