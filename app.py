import streamlit as st
import pandas as pd
import os

# Constants
BATTLEFIELDS = 6
TOTAL_TROOPS = 120
FILENAME = "strategies.csv"
ADMIN_PASSWORD = "secret123"  # Change this to something secure

# Initialize CSV with headers if missing
if not os.path.exists(FILENAME):
    columns = ["Name"] + [f"B{i+1}" for i in range(BATTLEFIELDS)]
    pd.DataFrame(columns=columns).to_csv(FILENAME, index=False)

# App Title
st.title("🎖️ Colonel Blotto Game")

# Role selector
role = st.radio("Who are you?", ["Player", "Organizer"])

# PLAYER VIEW
if role == "Player":
    name = st.text_input("Enter your name")

    if name.strip() != "":
        try:
            df = pd.read_csv(FILENAME)
            existing = df[df["Name"] == name]
            if not existing.empty:
                st.success("✅ You have already submitted your strategy.")
                st.subheader("Your submitted strategy:")
                st.dataframe(existing.set_index("Name"))
                st.stop()
        except (pd.errors.EmptyDataError, FileNotFoundError):
            pass  # File may not exist yet

    # Show input fields only if not already submitted
    alloc = [st.number_input(f"Battlefield {i+1}", min_value=0, value=0, step=1) for i in range(BATTLEFIELDS)]

    if st.button("Submit Strategy"):
        if name.strip() == "":
            st.error("Name cannot be empty.")
        elif sum(alloc) != TOTAL_TROOPS:
            st.error(f"Total troops must be exactly {TOTAL_TROOPS}. You entered {sum(alloc)}.")
        else:
            try:
                existing = pd.read_csv(FILENAME)
                if name in existing["Name"].values:
                    st.warning("You’ve already submitted. No changes allowed.")
                    st.stop()
                existing = existing[existing["Name"] != name]
            except (pd.errors.EmptyDataError, FileNotFoundError):
                existing = pd.DataFrame(columns=["Name"] + [f"B{i+1}" for i in range(BATTLEFIELDS)])

            new_entry = pd.DataFrame([[name] + alloc], columns=["Name"] + [f"B{i+1}" for i in range(BATTLEFIELDS)])
            df = pd.concat([existing, new_entry], ignore_index=True)
            df.to_csv(FILENAME, index=False)
            st.success("✅ Strategy submitted! Thank you for participating.")
            st.subheader("Your submitted strategy:")
            st.dataframe(new_entry.set_index("Name"))
            st.stop()

    # Show rankings if unlocked
    if os.path.exists("show_results.txt"):
        st.subheader("🏆 Final Rankings")
        try:
            df = pd.read_csv(FILENAME)
            names = df["Name"].tolist()
            strategies = df.iloc[:, 1:].values.tolist()
            n_players = len(strategies)
            n_battlefields = len(strategies[0])

            scores = {name: 0 for name in names}

            for i in range(n_players):
                total_battlefield_wins = 0
                for j in range(n_players):
                    if i == j:
                        continue
                    s1, s2 = strategies[i], strategies[j]
                    wins = sum(a > b for a, b in zip(s1, s2))
                    total_battlefield_wins += wins
                scores[names[i]] = round(total_battlefield_wins / (n_players - 1), 2)

            rankings = pd.DataFrame(scores.items(), columns=["Player", "Avg Battlefields Won"])
            rankings = rankings.sort_values(by="Avg Battlefields Won", ascending=False).reset_index(drop=True)
            st.dataframe(rankings)

        except Exception as e:
            st.error(f"Error calculating rankings: {e}")

# ORGANIZER VIEW
elif role == "Organizer":
    pw = st.text_input("Enter organizer password", type="password")
    if pw == ADMIN_PASSWORD:
        st.success("Organizer access granted ✅")

        # Load strategies
        try:
            data = pd.read_csv(FILENAME)
            if not data.empty:
                st.subheader("📋 Submitted Strategies")
                st.dataframe(data)
            else:
                st.info("No players have submitted yet.")
        except pd.errors.EmptyDataError:
            st.info("Waiting for submissions...")

        # Rankings logic
        def compare(s1, s2):
            wins1 = sum(a > b for a, b in zip(s1, s2))
            wins2 = sum(b > a for a, b in zip(s1, s2))
            return (1, 0) if wins1 > wins2 else (0, 1) if wins1 < wins2 else (0.5, 0.5)

        if st.button("🔓 Show Final Rankings to Everyone"):
            with open("show_results.txt", "w") as f:
                f.write("true")
            try:
                df = pd.read_csv(FILENAME)
                names = df["Name"].tolist()
                strategies = df.iloc[:, 1:].values.tolist()
                n_players = len(strategies)
                n_battlefields = len(strategies[0])

                scores = {name: 0 for name in names}

                for i in range(n_players):
                    total_battlefield_wins = 0
                    for j in range(n_players):
                        if i == j:
                            continue
                        s1, s2 = strategies[i], strategies[j]
                        wins = sum(a > b for a, b in zip(s1, s2))
                        total_battlefield_wins += wins
                    # Average battlefields won per opponent
                    scores[names[i]] = round(total_battlefield_wins / (n_players - 1), 2)

                rankings = pd.DataFrame(scores.items(), columns=["Player", "Avg Battlefields Won"])
                rankings = rankings.sort_values(by="Avg Battlefields Won", ascending=False).reset_index(drop=True)

                st.subheader("🏆 Final Rankings")
                st.dataframe(rankings)

            except Exception as e:
                st.error(f"Error calculating rankings: {e}")


                
        if st.button("🗑️ Reset All Submissions"):
            columns = ["Name"] + [f"B{i+1}" for i in range(BATTLEFIELDS)]
            pd.DataFrame(columns=columns).to_csv(FILENAME, index=False)
            st.success("All submissions have been reset. Ready for a new round!")

    else:
        if pw:
            st.error("Incorrect password.")
