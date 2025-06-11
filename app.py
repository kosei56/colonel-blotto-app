import streamlit as st
import pandas as pd
import os

# Constants
BATTLEFIELDS = 5
TOTAL_TROOPS = 100
FILENAME = "strategies.csv"

st.title("🎖️ Colonel Blotto Game")

# User input
name = st.text_input("Enter your name")
alloc = [st.number_input(f"Battlefield {i+1}", min_value=0, value=0, step=1) for i in range(BATTLEFIELDS)]

if st.button("Submit Strategy"):
    if sum(alloc) != TOTAL_TROOPS:
        st.error(f"Total troops must be exactly {TOTAL_TROOPS}. You entered {sum(alloc)}.")
    elif name.strip() == "":
        st.error("Name cannot be empty.")
    else:
        # Save strategy
        df = pd.DataFrame([[name] + alloc], columns=["Name"] + [f"B{i+1}" for i in range(BATTLEFIELDS)])
        if os.path.exists(FILENAME):
            existing = pd.read_csv(FILENAME)
            existing = existing[existing["Name"] != name]  # Overwrite by name
            df = pd.concat([existing, df], ignore_index=True)
        df.to_csv(FILENAME, index=False)
        st.success("Strategy submitted!")

# Show current players
if os.path.exists(FILENAME):
    st.subheader("📋 Current Players")
    data = pd.read_csv(FILENAME)
    st.dataframe(data)

# Compute rankings
def compare(s1, s2):
    wins1 = sum(a > b for a, b in zip(s1, s2))
    wins2 = sum(b > a for a, b in zip(s1, s2))
    return (1, 0) if wins1 > wins2 else (0, 1) if wins1 < wins2 else (0.5, 0.5)

if st.button("Calculate Rankings"):
    if os.path.exists(FILENAME):
        df = pd.read_csv(FILENAME)
        names = df["Name"]
        strategies = df.iloc[:, 1:].values.tolist()
        scores = {name: 0 for name in names}

        for i in range(len(strategies)):
            for j in range(i+1, len(strategies)):
                s1, s2 = strategies[i], strategies[j]
                name1, name2 = names[i], names[j]
                r1, r2 = compare(s1, s2)
                scores[name1] += r1
                scores[name2] += r2

        rankings = pd.DataFrame(scores.items(), columns=["Player", "Score"]).sort_values(by="Score", ascending=False)
        st.subheader("🏆 Rankings")
        st.dataframe(rankings.reset_index(drop=True))
