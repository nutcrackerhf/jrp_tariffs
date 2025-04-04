# Import python packages
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Mundell-Fleming Simulator", layout="wide")

st.title("\U0001F4CA JRP Tariff Effects Model")
st.markdown("""
This interactive app lets you explore the effects of tariffs and policy responses on output, interest rates, and the exchange rate
using a simplified Mundell-Fleming framework (flexible exchange rates, high capital mobility).
""")


# --- Sidebar Inputs ---
st.sidebar.header("Model Assumptions")

tariff_shock = st.sidebar.slider("Tariff Shock (reduction in imports, % of GDP)", 0.0, 5.0, 2.0)
ad_contraction = st.sidebar.slider("Aggregate Demand Drag (% of GDP)", 0.0, 5.0, 1.0)
fiscal_response = st.sidebar.selectbox("Fiscal Response (What Does Gov do with Tariff Revenue)", ["Neutral", "Debt Paydown (Contractionary)", "Tax Cut (Mildly Expansionary)"])
monetary_policy = st.sidebar.selectbox("Monetary Policy Reaction", ["Neutral", "Eases Rates", "Tightens Rates"])

st.sidebar.markdown("""The IS curve shows how output (Y) responds to changes in the interest rate (r), assuming goods market equilibrium. It reflects how:

-  Higher interest rates discourage business investment and consumer borrowing (especially for durables).

-  Lower interest rates encourage more borrowing and spending.

A point along the curve represents an equilibrium between output and rates, where Total Demand = Total Output.""")

st.sidebar.markdown("""The LM curve shows how the interest rate (r) must adjust to maintain equilibrium in the money market, given a level of output (Y).

Key idea:

-  Higher output → more transactions → greater demand for money.

-  If the money supply is fixed, this higher demand pushes up interest rates to ration money.

-  So: More activity → higher interest rates to clear the market.

""")

# --- Core Model Setup ---
# Base values for IS-LM-BP intersections (arbitrary units)
Y0 = 100
r0 = 4.0  # base interest rate
E0 = 1.0  # base exchange rate index

# any shock that affects aggregate demand will shift the IS curve.
# positive shock to Y from increase in net exports will shift IS curve to the right
# net exports do not go up exactly by the decline in imports, due to imperfect/suboptimal import substitution

# Define shock adjustments
# IS curve shifts
net_exports_boost = tariff_shock * 0.6  # only partial pass-through to net exports
fiscal_shift = 0
if fiscal_response == "Debt Paydown (Contractionary)":
    fiscal_shift = -1.0
elif fiscal_response == "Tax Cut (Mildly Expansionary)":
    fiscal_shift = 0.5

# so better net exports help IS line move right (more output at a given rate)
# we directly subtract the drop in GDP (ad_contraction) which shifts the IS line to the left
# the fiscal response (option) says What does the government do with the tariff revenue?


IS_shift = net_exports_boost - ad_contraction + fiscal_shift


# ok, now, in a world of higher output, 
# If the central bank doesn’t increase the money supply, 
# interest rates must rise to ration available liquidity.


# Easing (rate cuts, QE): More liquidity → interest rates can be lower at every level of output 
# → LM shifts down/right.

#Tightening: Less liquidity → interest rates must be higher to ration money → 
# LM shifts up/left.

# LM curve shift from monetary policy
LM_shift = 0
if monetary_policy == "Eases Rates":
    LM_shift = 1.0
elif monetary_policy == "Tightens Rates":
    LM_shift = -1.0

# Compute new equilibrium
# output is strongly responsive to demand-side shocks, so coefficient is 0.8
# smaller coefficient for LM than IS because monetary transmission takes time, 
# and not all sectors respond equally


Y_new = Y0 + 0.8 * IS_shift + 0.5 * LM_shift
r_new = r0 - 0.3 * LM_shift + 0.2 * IS_shift
E_change = -0.5 * (r0 - r_new) + 0.3 * net_exports_boost  # simplified FX equation
E_new = E0 + E_change

# --- Display Results ---
st.subheader("Results")
col1, col2, col3 = st.columns(3)
col1.metric("Output (Y)", f"{Y_new:.2f}", delta=f"{Y_new - Y0:+.2f}")
col2.metric("Interest Rate (r)", f"{r_new:.2f}%", delta=f"{r_new - r0:+.2f}%")
col3.metric("Exchange Rate (E)", f"{E_new:.2f}", delta=f"{E_new - E0:+.2f}")


# --- Dynamic Narrative Summary ---
st.subheader("Narrative")

description = []

# Tariff effects
tariff_text = f"A tariff shock of {tariff_shock:.1f}% of GDP boosts net exports by {net_exports_boost:.1f}%, which tends to increase output and support the exchange rate."
description.append(tariff_text)

# AD drag
if ad_contraction > 0:
    ad_text = f"However, higher prices lead to an aggregate demand contraction of {ad_contraction:.1f}% of GDP, offsetting some of the initial boost."
    description.append(ad_text)

# Fiscal policy
descriptions_map = {
    "Debt Paydown (Contractionary)": "The government uses tariff revenue to pay down debt, which is contractionary and further reduces output.",
    "Tax Cut (Mildly Expansionary)": "The government implements a mild tax cut, providing a partial offset to weaker demand.",
    "Neutral": "There is no significant fiscal policy change."
}
description.append(descriptions_map[fiscal_response])

# Monetary policy
monetary_map = {
    "Neutral": "The central bank does not respond, leaving the interest rate relatively unchanged.",
    "Eases Rates": "The central bank eases monetary policy, lowering interest rates and stimulating output.",
    "Tightens Rates": "The central bank tightens policy, raising interest rates and reducing output."
}
description.append(monetary_map[monetary_policy])

# FX summary
if E_change > 0:
    fx_outcome = "On net, the exchange rate is expected to strengthen due to improving net exports and/or higher interest rates."
elif E_change < 0:
    fx_outcome = "On net, the exchange rate is expected to weaken due to lower interest rates or weaker domestic demand."
else:
    fx_outcome = "The exchange rate is expected to remain broadly stable, as opposing forces balance out."
description.append(fx_outcome)

st.write(" ".join(description))

# --- Plot IS-LM Curves using Plotly ---
Y_vals = np.linspace(95, 105, 100)
IS_curve = r0 - 0.5 * (Y_vals - Y0) + IS_shift
LM_curve = r0 + 0.7 * (Y_vals - Y0) + LM_shift

fig = go.Figure()
fig.add_trace(go.Scatter(x=Y_vals, y=IS_curve, mode='lines', name='IS Curve', line=dict(width=3)))
fig.add_trace(go.Scatter(x=Y_vals, y=LM_curve, mode='lines', name='LM Curve', line=dict(width=3)))
fig.add_trace(go.Scatter(x=[Y_new], y=[r_new], mode='markers', name='Equilibrium', marker=dict(size=10, color='red')))

fig.update_layout(
    title="IS-LM Diagram (Flexible Exchange Rates)",
    xaxis_title="Output (Y)",
    yaxis_title="Interest Rate (r)",
    legend=dict(x=0.02, y=0.98),
    margin=dict(l=40, r=40, t=40, b=40),
    template="plotly_white",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# --- Optional Table ---
st.subheader("Underlying Shocks")
data = {
    "Component": ["Tariff Shock (NX Boost)", "AD Contraction", "Fiscal Shift", "Monetary Shift"],
    "Value (% of GDP or Rate Shift)": [net_exports_boost, -ad_contraction, fiscal_shift, LM_shift]
}
df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

# --- Coefficient Reference Table ---
with st.expander("Show Model Coefficients and Interpretations"):
    coeff_data = {
        "Coefficient": [
            "0.8 (IS effect on → Y)",
            "0.5 (LM → Y)",
            "-0.3 (LM → r)",
            "0.2 (IS → r)",
            "-0.5 (∆r → ∆E)",
            "0.3 (NX → ∆E)"
        ],
        "Meaning": [
            "Effect of demand shocks on output (fiscal multiplier)",
            "Effect of monetary easing on output",
            "Effect of monetary easing on interest rates",
            "Effect of demand pressure on interest rates",
            "Effect of interest rate changes on exchange rate",
            "Effect of net export boost on exchange rate"
        ]
    }
    coeff_df = pd.DataFrame(coeff_data)
    st.dataframe(coeff_df, use_container_width=True)

st.caption("Note: This is a simplified linearized Mundell-Fleming simulation with arbitrary scale for illustrative purposes.")
