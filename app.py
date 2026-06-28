import streamlit as st
import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, value

# 1. Define Core Problem Parameters
ingredients = ["Chicken", "Beef", "Mutton", "Rice", "Wheat bran", "Gel"]

costs = {
    "Chicken": 0.013, "Beef": 0.008, "Mutton": 0.010,
    "Rice": 0.002, "Wheat bran": 0.005, "Gel": 0.001
}

protein = {
    "Chicken": 0.100, "Beef": 0.200, "Mutton": 0.150,
    "Rice": 0.000, "Wheat bran": 0.040, "Gel": 0.000
}

fat = {
    "Chicken": 0.080, "Beef": 0.100, "Mutton": 0.110,
    "Rice": 0.010, "Wheat bran": 0.010, "Gel": 0.000
}

fibre = {
    "Chicken": 0.001, "Beef": 0.005, "Mutton": 0.003,
    "Rice": 0.100, "Wheat bran": 0.150, "Gel": 0.000
}

salt = {
    "Chicken": 0.002, "Beef": 0.005, "Mutton": 0.007,
    "Rice": 0.002, "Wheat bran": 0.008, "Gel": 0.000
}

# 2. Initialize PuLP Model
model = LpProblem("Whiskas_Blending_Optimization", LpMinimize)

# 3. Decision Variables (Grams of each ingredient)
x = LpVariable.dicts("Ingr", ingredients, lowBound=0, cat="Continuous")

# 4. Objective Function: Minimize Total Cost
model += lpSum(costs[i] * x[i] for i in ingredients), "Total_Cost"

# 5. Constraints
model += lpSum(x[i] for i in ingredients) == 100.0, "Total_Weight_100g"
model += lpSum(protein[i] * x[i] for i in ingredients) >= 8.0, "Min_Protein"
model += lpSum(fat[i] * x[i] for i in ingredients) >= 6.0, "Min_Fat"
model += lpSum(fibre[i] * x[i] for i in ingredients) <= 2.0, "Max_Fibre"
model += lpSum(salt[i] * x[i] for i in ingredients) <= 0.4, "Max_Salt"

# 6. Solve
model.solve()
