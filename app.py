# app.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from calculator import (
    calculate_bunker_cost, calculate_tce, get_vessel_specs, 
    calculate_speed_duration, calculate_freight_rate_from_ws,
    generate_sensitivity_matrix, VESSEL_SPECS, STANDARD_ROUTES
)

st.set_page_config(page_title="Tanker Freight & TCE Dashboard", layout="wide")

st.title("Tanker Freight & TCE Dashboard")
st.write("Decision-support tool for tanker economics & chartering analytics.")

# Sidebar Configuration
st.sidebar.header("1. Benchmark Route Selection")
route_name = st.sidebar.selectbox("Standard Route", list(STANDARD_ROUTES.keys()))
route_info = STANDARD_ROUTES[route_name]

# Vessel Class Selection
vessel_type = st.sidebar.selectbox(
    "Vessel Class", 
    list(VESSEL_SPECS.keys()), 
    index=list(VESSEL_SPECS.keys()).index(route_info["vessel_class"])
)
specs = get_vessel_specs(vessel_type)
st.sidebar.caption(specs["description"])

st.sidebar.header("2. Voyage & Pricing Inputs")

pricing_mode = st.sidebar.radio("Freight Pricing Mode", ["Worldscale (WS)", "Flat $/mt Rate"])

if pricing_mode == "Worldscale (WS)":
    ws_points = st.sidebar.number_input("Worldscale Points (WS)", value=100.0, step=2.5)
    ws_flat_rate = st.sidebar.number_input("WS Flat Rate ($/mt)", value=route_info["ws_flat_rate"], step=0.5)
    freight_rate = calculate_freight_rate_from_ws(ws_points, ws_flat_rate)
    st.sidebar.info(f"Calculated Freight Rate: **${freight_rate:.2f} / mt**")
else:
    freight_rate = st.sidebar.number_input("Freight Rate ($/mt)", value=15.0, step=0.5)

cargo_qty = st.sidebar.number_input("Cargo Quantity (mt)", value=specs["capacity_dwt"], step=5000.0)
fuel_price = st.sidebar.number_input("VLSFO Fuel Price ($/mt)", value=600.0, step=10.0)
port_costs = st.sidebar.number_input("Port & Canal Expenses ($)", value=route_info["port_costs"], step=5000.0)

# Speed & Distance
speed_knots = st.sidebar.slider("Vessel Speed (knots)", min_value=10.0, max_value=16.0, value=12.5, step=0.5)
distance_nm = st.sidebar.number_input("Round Trip Distance (NM)", value=route_info["distance_nm"], step=200)
days_at_sea = calculate_speed_duration(distance_nm, speed_knots)
days_in_port = st.sidebar.number_input("Days in Port / Waiting", value=route_info["port_days"], step=0.5)
total_days = days_at_sea + days_in_port

# Perform Calculations
bunker_cost = calculate_bunker_cost(
    days_at_sea=days_at_sea, 
    sea_cons=specs["sea_cons"], 
    days_in_port=days_in_port, 
    port_cons=specs["port_cons"], 
    fuel_price=fuel_price
)

gross_revenue = freight_rate * cargo_qty
net_profit = gross_revenue - port_costs - bunker_cost
tce_result = calculate_tce(
    freight_rate=freight_rate,
    cargo_qty=cargo_qty,
    port_costs=port_costs,
    bunker_cost=bunker_cost,
    total_days=total_days
)

# Display Key Metrics
st.subheader("Financial Summary & KPIs")
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(label="Gross Revenue", value=f"${gross_revenue:,.0f}")
with m2:
    st.metric(label="Bunker Fuel Cost", value=f"${bunker_cost:,.0f}")
with m3:
    st.metric(label="Net Voyage Profit", value=f"${net_profit:,.0f}")
with m4:
    st.metric(label="Estimated TCE (Net/Day)", value=f"${tce_result:,.0f} / day")

st.divider()

# Tabs Layout
tab1, tab2 = st.tabs(["Revenue & Cost Waterfall", "Sensitivity Analysis Matrix"])

with tab1:
    st.write("### Financial Breakdown (Waterfall Chart)")
    fig = go.Figure(go.Waterfall(
        name="TCE Breakdown",
        orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["Gross Revenue", "Port Expenses", "Bunker Expenses", "Net Voyage Profit"],
        textposition="outside",
        text=[f"+${gross_revenue:,.0f}", f"-${port_costs:,.0f}", f"-${bunker_cost:,.0f}", f"${net_profit:,.0f}"],
        y=[gross_revenue, -port_costs, -bunker_cost, net_profit],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#EF553B"}},
        increasing={"marker": {"color": "#00CC96"}},
        totals={"marker": {"color": "#636EFA"}}
    ))
    fig.update_layout(title="Voyage Cash Flow Waterfall", showlegend=False, height=500)
    st.plotly_chart(fig, width="stretch")

with tab2:
    st.write("### TCE Sensitivity Matrix ($/day)")
    st.caption("Evaluates TCE outcome across varying Freight Rates (Rows) and Fuel Prices (Columns).")
    
    sens_df = generate_sensitivity_matrix(
        base_freight=freight_rate,
        base_fuel_price=fuel_price,
        cargo_qty=cargo_qty,
        port_costs=port_costs,
        days_at_sea=days_at_sea,
        sea_cons=specs["sea_cons"],
        days_in_port=days_in_port,
        port_cons=specs["port_cons"],
        total_days=total_days
    )
    
    fig_heat = px.imshow(
        sens_df,
        labels=dict(x="Fuel Price ($/mt)", y="Freight Rate ($/mt)", color="TCE ($/day)"),
        text_auto=".0f",
        color_continuous_scale="RdYlGn"
    )
    fig_heat.update_layout(height=500)
    st.plotly_chart(fig_heat, width="stretch")