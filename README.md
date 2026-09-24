# Tanker Freight & TCE Analytics Dashboard

An interactive decision-support tool designed for crude oil chartering and trading desks (e.g., TotalEnergies / BxT Trading) to evaluate voyage profitability, convert Worldscale benchmark rates, and perform sensitivity analysis.

## Key Features
* **Worldscale (WS) Conversion:** Dynamically calculates effective freight rates ($/mt) and gross voyage revenue.
* **Voyage Economics & TCE Engine:** Calculates net daily Time Charter Equivalent ($/day) factoring in sea/port durations and VLSFO bunker fuel consumption.
* **Waterfall Cost Breakdown:** Interactive Plotly visual degradation from gross revenue to net voyage profit.
* **Multi-Variable Sensitivity Matrix:** Heatmap assessing TCE outcomes under varying freight rates (+/-30%) and bunker fuel prices (+/-30%).

## Tech Stack
* **Language:** Python 3.10+
* **Framework:** Streamlit
* **Data & Analytics:** Pandas, NumPy, Plotly

## Local Installation & Running

1. Clone the repository:
git clone [https://github.com/AlexisGpro/tanker-freight-tce-dashboard.git](https://github.com/AlexisGpro/tanker-freight-tce-dashboard.git)
cd tanker-freight-tce-dashboard

2. Install dependencies:
pip install -r requirements.txt

3. Run the Streamlit dashboard:
streamlit run app.py

## Technical Report
A full LaTeX engineering report detailing the mathematical formulation and financial models is available in the docs/ directory.