# calculator.py
import numpy as np
import pandas as pd

# Specifications by vessel class
VESSEL_SPECS = {
    "VLCC": {
        "description": "Very Large Crude Carrier (~2 million barrels)",
        "capacity_dwt": 270000.0,
        "sea_cons": 45.0,
        "port_cons": 5.0
    },
    "Suezmax": {
        "description": "Max capacity for Suez Canal (~1 million barrels)",
        "capacity_dwt": 150000.0,
        "sea_cons": 32.0,
        "port_cons": 4.0
    },
    "Aframax": {
        "description": "Flexible regional trader (~700,000 barrels)",
        "capacity_dwt": 100000.0,
        "sea_cons": 25.0,
        "port_cons": 3.0
    }
}

# Standard Benchmark Routes
STANDARD_ROUTES = {
    "Custom / Manual": {
        "vessel_class": "VLCC",
        "distance_nm": 6000,
        "port_days": 4.0,
        "port_costs": 120000.0,
        "ws_flat_rate": 20.0
    },
    "TD3C (MEG -> China)": {
        "vessel_class": "VLCC",
        "distance_nm": 6700,
        "port_days": 4.0,
        "port_costs": 150000.0,
        "ws_flat_rate": 22.50
    },
    "TD20 (WAF -> UK-Continent)": {
        "vessel_class": "Suezmax",
        "distance_nm": 4800,
        "port_days": 3.5,
        "port_costs": 110000.0,
        "ws_flat_rate": 18.20
    },
    "TD7 (UK-Continent -> US Gulf)": {
        "vessel_class": "Aframax",
        "distance_nm": 3600,
        "port_days": 3.0,
        "port_costs": 95000.0,
        "ws_flat_rate": 16.80
    }
}


def get_vessel_specs(vessel_type: str) -> dict:
    """Retrieve specifications for a given vessel class."""
    return VESSEL_SPECS.get(vessel_type, VESSEL_SPECS["VLCC"])


def calculate_speed_duration(distance_nm: float, speed_knots: float) -> float:
    """Calculate sea days based on distance in nautical miles and vessel speed."""
    if speed_knots <= 0:
        return 0.0
    hours = (distance_nm * 2) / speed_knots  # Round trip (laden + ballast)
    return hours / 24.0


def calculate_freight_rate_from_ws(ws_points: float, flat_rate: float) -> float:
    """Calculate Worldscale freight rate in $/mt from WS points and Flat Rate."""
    return (ws_points / 100.0) * flat_rate


def calculate_bunker_cost(days_at_sea: float, sea_cons: float, 
                         days_in_port: float, port_cons: float, 
                         fuel_price: float) -> float:
    """Calculate total bunker fuel expenditure for the voyage."""
    total_fuel_tons = (days_at_sea * sea_cons) + (days_in_port * port_cons)
    return total_fuel_tons * fuel_price


def calculate_tce(freight_rate: float, cargo_qty: float, 
                  port_costs: float, bunker_cost: float, 
                  total_days: float) -> float:
    """Calculate the Time Charter Equivalent (TCE) in USD/day."""
    gross_revenue = freight_rate * cargo_qty
    net_revenue = gross_revenue - port_costs - bunker_cost
    
    if total_days <= 0:
        return 0.0
        
    return net_revenue / total_days


def generate_sensitivity_matrix(base_freight: float, base_fuel_price: float, 
                                 cargo_qty: float, port_costs: float, 
                                 days_at_sea: float, sea_cons: float, 
                                 days_in_port: float, port_cons: float, 
                                 total_days: float) -> pd.DataFrame:
    """Generate a TCE sensitivity matrix varying Freight Rates and Fuel Prices."""
    freight_steps = np.linspace(base_freight * 0.7, base_freight * 1.3, 5)
    fuel_steps = np.linspace(base_fuel_price * 0.7, base_fuel_price * 1.3, 5)
    
    matrix = np.zeros((len(freight_steps), len(fuel_steps)))
    
    for i, fr in enumerate(freight_steps):
        for j, fp in enumerate(fuel_steps):
            b_cost = calculate_bunker_cost(days_at_sea, sea_cons, days_in_port, port_cons, fp)
            matrix[i, j] = calculate_tce(fr, cargo_qty, port_costs, b_cost, total_days)
            
    return pd.DataFrame(
        matrix, 
        index=[f"${fr:.1f}/mt" for fr in freight_steps],
        columns=[f"${fp:.0f}/t" for fp in fuel_steps]
    )