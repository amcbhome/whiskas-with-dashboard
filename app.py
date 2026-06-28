import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, value

# Set page configuration
st.set_page_config(
    page_title="Whiskas Mix Optimizer",
    page_icon="🐱",
    layout="wide"
)

# Custom CSS to handle layout heights cleanly
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px; }
    .css-1r6g72q { font-size: 14px; }
    </style>
""", unsafe_scale=True)

st.title("🐱 Whiskas Least-Cost Product Blending Dashboard")
st.markdown("Optimized recipe formulation for a 100g can of cat food meeting strict nutritional targets.")

# --- DATA CONFIGURATION --- 
ingredients = ["Chicken", "Beef", "Mutton", "Rice", "Wheat bran", "Gel"]
costs = {"Chicken": 0.013, "Beef": 0.008, "Mutton": 0.010, "Rice": 0.002, "Wheat bran": 0.005, "Gel": 0.001}
protein = {"Chicken": 0.100, "Beef": 0.200, "Mutton": 0.150, "Rice": 0.000, "Wheat bran": 0.040, "Gel": 0.000}
fat = {"Chicken": 0.080, "Beef": 0.100, "Mutton": 0.110, "Rice": 0.010, "Wheat bran": 0.010, "Gel": 0.000}
fibre = {"Chicken": 0.001, "Beef": 0.005, "Mutton": 0.003, "Rice": 0.100, "Wheat bran": 0.150, "Gel": 0.000}
salt = {"Chicken": 0.002, "Beef": 0.005, "Mutton": 0.007, "Rice": 0.002, "Wheat bran": 0.008, "Gel": 0.000}

# --- SIDEBAR TARGET CONTROLS --- 
st.sidebar.header("Nutritional Targets (per 100g)")
min_protein = st.sidebar.number_input("Min Protein (g)", value=8.0, step=0.5)
min_fat = st.sidebar.number_input("Min Fat (g)", value=6.0, step=0.5)
max_fibre = st.sidebar.number_input("Max Fibre (g)", value=2.0, step=0.1)
max_salt = st.sidebar.number_input("Max Salt (g)", value=0.4, step=0.05)

# --- PULP OPTIMIZATION MODEL ---
model = LpProblem("Whiskas_Optimization", LpMinimize)
x = LpVariable.dicts("Ingr", ingredients, lowBound=0, cat="Continuous")

# Objective Function 
model += lpSum(costs[i] * x[i] for i in ingredients)

# Constraints 
model += lpSum(x[i] for i in ingredients) == 100.0, "TotalWeight"
model += lpSum(protein[i] * x[i] for i in ingredients) >= min_protein, "Protein"
model += lpSum(fat[i] * x[i] for i in ingredients) >= min_fat, "Fat"
model += lpSum(fibre[i] * x[i] for i in ingredients) <= max_fibre, "Fibre"
model += lpSum(salt[i] * x[i] for i in ingredients) <= max_salt, "Salt"

# Solve
model.solve()

# --- PARSE METRICS ---
total_cost = value(model.objective)
calculated_protein = sum(protein[i] * x[i].value() for i in ingredients)
calculated_fat = sum(fat[i] * x[i].value() for i in ingredients)
calculated_fibre = sum(fibre[i] * x[i].value() for i in ingredients)
calculated_salt = sum(salt[i] * x[i].value() for i in ingredients)

# ==========================================
# ROW 1: TOP KEY FINANCIAL PERFORMANCE METRICS
# ==========================================
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Optimization Status", value=LpStatus[model.status])
with m2:
    st.metric(label="Min Total Cost", value=f"£{total_cost:.4f}")
with m3:
    st.metric(label="Total Batch Mass", value="100.00g")
with m4:
    st.metric(label="Cost Per Gram", value=f"£{total_cost/100:.5f}")

st.markdown("---")

# ==========================================
# ROW 2: INGREDIENT MIX PRODUCT DIALS (1/4 HEIGHT)
# ==========================================
st.subheader("📋 Ingredient Product Mix Dials")

# Create 6 parallel columns for each ingredient dial
dial_cols = st.columns(6)

def generate_gauge_dial(name, current_val):
    """Generates a clean semi-circular ring dial tracking percentages up to 100%"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_val,
        number={'suffix': "%", 'font': {'size': 22, 'color': '#2E7D32' if current_val > 0 else '#757575'}},
        title={'text': f"<b>{name}</b> Mix", 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "gray", 'visible': False},
            'bar': {'color': "#4CAF50" if current_val > 0 else "#E0E0E0", 'thickness': 1},
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "#BDBDBD",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(239, 83, 80, 0.1)' if current_val > 0 else 'white'},
                {'range': [60, 85], 'color': 'rgba(255, 167, 38, 0.1)' if current_val > 0 else 'white'},
                {'range': [85, 100], 'color': 'rgba(76, 175, 80, 0.1)' if current_val > 0 else 'white'}
            ]
        }
    ))
    # Compact height and removes unnecessary layout margins
    fig.update_layout(
        height=140, 
        margin=dict(l=10, r=10, t=35, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# Map values dynamically to the UI columns
for idx, name in enumerate(ingredients):
    with dial_cols[idx]:
        raw_val = x[name].value()
        percentage_val = float(raw_val) if (raw_val and raw_val > 1e-5) else 0.0
        
        # Display the custom Plotly gauge
        st.plotly_chart(generate_gauge_dial(name, percentage_val), use_container_width=True, key=f"dial_{name}")
        
        # Display a green checkmark indicating active inclusion or an empty indicator
        if percentage_val > 0.0:
            st.markdown(f"<p style='text-align: center; color: #2E7D32; font-weight: bold; margin-top: -15px;'>✔ Active ({percentage_val:.1f}g)</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align: center; color: #9E9E9E; margin-top: -15px;'>✕ Omitted (0.0g)</p>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# ROW 3: DETAILED COMPOSITION & BREAKDOWNS
# ==========================================
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📍 Recipe Allocation Details")
    recipe_data = []
    for i in ingredients:
        amt = x[i].value()
        recipe_data.append({
            "Ingredient": i,
            "Mass Allocated": amt if amt > 1e-5 else 0.0,
            "Cost Contribution": (amt * costs[i]) if amt > 1e-5 else 0.0
        })
    df_recipe = pd.DataFrame(recipe_data)
    
    st.dataframe(
        df_recipe.style.format({
            "Mass Allocated": "{:.2f}g",
            "Cost Contribution": "£{:.4f}"
        }),
        use_container_width=True,
        hide_index=True
    )

with col_right:
    st.subheader("🧪 Nutrient Constraints Validation")
    nutri_data = {
        "Nutrient Metric": ["Protein", "Fat", "Fibre", "Salt"],
        "Direction": [">=", ">=", "<=", "<="],
        "Threshold Limit": [min_protein, min_fat, max_fibre, max_salt],
        "Actual Recipe Amount": [calculated_protein, calculated_fat, calculated_fibre, calculated_salt]
    }
    df_nutri = pd.DataFrame(nutri_data)
    
    st.dataframe(
        df_nutri.style.format({
            "Threshold Limit": "{:.2f}g",
            "Actual Recipe Amount": "{:.2f}g"
        }),
        use_container_width=True,
        hide_index=True
    )
