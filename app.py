import streamlit as st
import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, value

# Set page layout to wide
st.set_page_config(page_title="Whiskas Mix Optimizer", page_icon="🐱", layout="wide")

st.title("🐱 Whiskas Least-Cost Product Blending Dashboard")
st.markdown("""
This analytics application determines the most cost-efficient ingredient formula for a **100g can of cat food**, 
while satisfying all minimum and maximum chemical nutrient requirements.
""")

# --- INPUT DATA SETUP ---
ingredients = ["Chicken", "Beef", "Mutton", "Rice", "Wheat bran", "Gel"]
costs = {"Chicken": 0.013, "Beef": 0.008, "Mutton": 0.010, "Rice": 0.002, "Wheat bran": 0.005, "Gel": 0.001}
protein = {"Chicken": 0.100, "Beef": 0.200, "Mutton": 0.150, "Rice": 0.000, "Wheat bran": 0.040, "Gel": 0.000}
fat = {"Chicken": 0.080, "Beef": 0.100, "Mutton": 0.110, "Rice": 0.010, "Wheat bran": 0.010, "Gel": 0.000}
fibre = {"Chicken": 0.001, "Beef": 0.005, "Mutton": 0.003, "Rice": 0.100, "Wheat bran": 0.150, "Gel": 0.000}
salt = {"Chicken": 0.002, "Beef": 0.005, "Mutton": 0.007, "Rice": 0.002, "Wheat bran": 0.008, "Gel": 0.000}

# --- SIDEBAR INTERFACE ---
st.sidebar.header("Nutritional Targets (per 100g)")
min_protein = st.sidebar.number_input("Min Protein (g)", value=8.0, step=0.5)
min_fat = st.sidebar.number_input("Min Fat (g)", value=6.0, step=0.5)
max_fibre = st.sidebar.number_input("Max Fibre (g)", value=2.0, step=0.1)
max_salt = st.sidebar.number_input("Max Salt (g)", value=0.4, step=0.05)

# --- MODEL PROCESSING ---
model = LpProblem("Whiskas_Optimization", LpMinimize)
x = LpVariable.dicts("Ingr", ingredients, lowBound=0, cat="Continuous")

# Objective function
model += lpSum(costs[i] * x[i] for i in ingredients)

# Constraints mapped dynamically from sidebar adjustments
model += lpSum(x[i] for i in ingredients) == 100.0, "TotalWeight"
model += lpSum(protein[i] * x[i] for i in ingredients) >= min_protein, "Protein"
model += lpSum(fat[i] * x[i] for i in ingredients) >= min_fat, "Fat"
model += lpSum(fibre[i] * x[i] for i in ingredients) <= max_fibre, "Fibre"
model += lpSum(salt[i] * x[i] for i in ingredients) <= max_salt, "Salt"

model.solve()

# --- METRIC COMPUTATIONS ---
total_cost = value(model.objective)
calculated_protein = sum(protein[i] * x[i].value() for i in ingredients)
calculated_fat = sum(fat[i] * x[i].value() for i in ingredients)
calculated_fibre = sum(fibre[i] * x[i].value() for i in ingredients)
calculated_salt = sum(salt[i] * x[i].value() for i in ingredients)

# --- KPI METRICS UI ---
st.subheader("Key Performance Indicators (KPIs)")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="Optimization Status", value=LpStatus[model.status])
with m2:
    st.metric(label="Minimum Batch Production Cost", value=f"£{total_cost:.4f} per can")
with m3:
    st.metric(label="Target Can Mass", value="100.00 grams")

st.markdown("---")

# --- VISUALIZATION ROW ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Optimal Ingredient Recipe Mix")
    
    # Structure Results Matrix
    recipe_data = []
    for i in ingredients:
        amt = x[i].value()
        recipe_data.append({
            "Ingredient": i,
            "Mass Allocated (g)": amt if amt > 1e-5 else 0.0,
            "Cost Contribution (£)": (amt * costs[i]) if amt > 1e-5 else 0.0
        })
    df_recipe = pd.DataFrame(recipe_data)
    
    # Clean styled interactive table view
    st.dataframe(
        df_recipe.style.format({
            "Mass Allocated (g)": "{:.2f}g",
            "Cost Contribution (£)": "£{:.4f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Donut configuration using native components
    st.markdown("**Recipe Composition Breakdown:**")
    st.bar_chart(df_recipe, x="Ingredient", y="Mass Allocated (g)", color="Ingredient")

with col_right:
    st.subheader("🧪 Chemical Composition Output")
    st.markdown("Actual nutritional density values versus strict thresholds.")

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
    
    # Visual check
    st.markdown("**Nutrient Concentration Profile:**")
    st.bar_chart(df_nutri, x="Nutrient Metric", y="Actual Recipe Amount")
