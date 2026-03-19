import streamlit as st
import random

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="CPL Pro: Cricket Premiere League", page_icon="🏏")

# --- 2. DATA: TEAMS & ROSTERS ---
INTER_TEAMS = {
    "India": ["Rohit", "Gill", "Kohli", "Iyer", "Rahul", "Hardik", "Jadeja", "Kuldeep", "Bumrah", "Shami", "Siraj"],
    "Australia": ["Warner", "Head", "Marsh", "Smith", "Labuschagne", "Maxwell", "Inglis", "Cummins", "Starc", "Zampa", "Hazlewood"],
    "England": ["Bairstow", "Malan", "Root", "Stokes", "Brook", "Buttler", "Livingstone", "Ali", "Woakes", "Rashid", "Wood"],
    "Pakistan": ["Fakhar", "Imam", "Babar", "Rizwan", "Shakeel", "Iftikhar", "Shadab", "Nawaz", "Shaheen", "Rauf", "Wasim"],
    "South Africa": ["De Kock", "Bavuma", "Van der Dussen", "Markram", "Klaasen", "Miller", "Jansen", "Coetzee", "Maharaj", "Rabada", "Ngidi"],
    "New Zealand": ["Conway", "Young", "Ravindra", "Mitchell", "Latham", "Phillips", "Neesham", "Santner", "Henry", "Boult", "Ferguson"],
    "Sri Lanka": ["Nissanka", "Perera", "Mendis", "Samarawickrama", "Asalanka", "Silva", "Wellalage", "Theekshana", "Madushanka", "Rajitha", "Pathirana"],
    "Afghanistan": ["Gurbaz", "Zadran", "Rahmat", "Shahidi", "Omarzai", "Nabi", "Rashid", "Mujeeb", "Naveen", "Farooqi", "Noor"],
    "Bangladesh": ["Litton", "Tanzid", "Shanto", "Hridoy", "Mushfiqur", "Mahmudullah", "Shakib", "Mehidy", "Taskin", "Shoriful", "Mustafizur"],
    "Netherlands": ["O'Dowd", "Singh", "Ackermann", "Sybrand", "Edwards", "de Leede", "Nidamanuru", "van Beek", "van der Merwe", "Dutt", "van Meekeren"]
}

NAT_TEAMS = {
    "Telangana": ["Vihari", "Thakur", "Milind", "Tanay", "Ravi", "Rakshann", "Pragnay", "Kartikeya", "Bhavesh", "Sankeerth", "Ajay"],
    "Maharashtra": ["Gaikwad", "Bawne", "Kazi", "Hangargekar", "Bachhav", "Palkar", "Chavan", "Ingale", "Nawale", "Ostwal", "Kothari"],
    "Karnataka": ["Agarwal", "Padikkal", "Pandey", "Nair", "Jose", "Gowtham", "Suchith", "Vyshak", "Kaushik", "Vidwath", "More"],
    "Tamil Nadu": ["Sai Sudharsan", "Jagadeesan", "Indrajith", "Shankar", "Shahrukh", "Washington", "Kishore", "Warrier", "Kulandai", "Sandeep", "Ajith"],
    "Delhi": ["Dhull", "Shorey", "Himmat", "Rana", "Lalit", "Pant", "Ishant", "Saini", "Hrithik", "Kuldip", "Mayank"],
    "Punjab": ["Abhishek", "Prabhsimran", "Anmolpreet", "Mandeep", "Wadhera", "Ramandeep", "Markande", "Arshdeep", "Kaul", "Baltej", "Gurnoor"],
    "Gujarat": ["Panchal", "Desai", "Urvil", "Chintan", "Arzan", "Hardik P", "Rishi", "Chawla", "Shen", "Tejas", "Manan"],
    "Rajasthan": ["Lamba", "Abhijeet", "Hooda", "Lomror", "Kunal", "Bishnoi", "Khaleel", "Deepak", "Aniket", "Kamlesh", "Tanveer"],
    "Uttar Pradesh": ["Madhav", "Samarth", "Juyal", "Rinku", "Jurel", "Saurabh", "Mavi", "Yash", "Kartik", "Rajpoot", "Kuldeep Y"],
    "Kerala": ["Kunnummal", "Prasad", "Samson", "Baby", "Vinod", "Gopal", "Thampi", "Vaisakh", "Warrier", "Midhun", "Nidheesh"]
}

# --- 3. INITIALIZE GAME STATE ---
if 'step' not in st.session_state:
    st.session_state.step = "menu"
    st.session_state.u_score = 0
    st.session_state.u_wickets = 0
    st.session_state.c_score = 0
    st.session_state.c_wickets = 0
    st.session_state.innings = 1
    st.session_state.target = 0
    st.session_state.u_team = ""
    st.session_state.c_team = ""
    st.session_state.u_roster = []
    st.session_state.c_roster = []
    st.session_state.logs = []

# --- 4. GAME INTERFACE ---

# SCREEN: MENU
if st.session_state.step == "menu":
    st.title("🏟️ CPL Pro: Cricket Premiere League")
    mode = st.radio("Select Tournament Mode:", ["International", "National"])
    if st.button("Proceed to Team Selection"):
        st.session_state.mode = mode
        st.session_state.step = "teams"
        st.rerun()

# SCREEN: TEAM SELECTION
elif st.session_state.step == "teams":
    st.header(f"🚩 Select Teams ({st.session_state.mode})")
    data = INTER_TEAMS if st.session_state.mode == "International" else NAT_TEAMS
    
    u_sel = st.selectbox("Your Team", list(data.keys()))
    c_sel = st.selectbox("Opponent Team (CPU)", [t for t in data.keys() if t != u_sel])
    
    if st.button("Confirm Teams"):
        st.session_state.u_team = u_sel
        st.session_state.c_team = c_sel
        st.session_state.u_roster = data[u_sel]
        st.session_state.c_roster = data[c_sel]
        st.session_state.step = "toss"
        st.rerun()

# SCREEN: TOSS
elif st.session_state.step == "toss":
    st.header("🪙 The Toss")
    choice = st.radio("Heads or Tails?", ["Heads", "Tails"])
    if st.button("Flip Coin"):
        toss_res = random.choice(["Heads", "Tails"])
        if choice == toss_res:
            st.success(f"It's {toss_res}! You won the toss and chose to Bat.")
        else:
            st.error(f"It's {toss_res}! You lost the toss. CPU put you in to Bat.")
        
        if st.button("Start 1st Innings"):
            st.session_state.step = "play"
            st.rerun()

# SCREEN: MATCHPLAY
elif st.session_state.step == "play":
    # --- INNINGS 1: USER BATTING ---
    if st.session_state.innings == 1:
        st.subheader(f"🏏 Batting: {st.session_state.u_team}")
        bat_name = st.session_state.u_roster[st.session_state.u_wickets]
        
        st.metric("Score", f"{st.session_state.u_score} / {st.session_state.u_wickets}")
        st.write(f"Current Batsman: **{bat_name}**")

        if st.button("🎲 Roll Dice"):
            u_dice, c_dice = random.randint(1, 6), random.randint(1, 6)
            st.write(f"You: {u_dice} | CPU: {c_dice}")
            
            if u_dice == c_dice:
                st.error(f"OUT! {bat_name} is gone!")
                st.session_state.u_wickets += 1
            else:
                st.session_state.u_score += u_dice
                st.success(f"Score! +{u_dice} runs")

            if st.session_state.u_wickets >= 10:
                st.session_state.target = st.session_state.u_score + 1
                st.session_state.innings = 2
                st.warning(f"Innings Over! Target for {st.session_state.c_team}: {st.session_state.target}")
            st.rerun()

    # --- INNINGS 2: USER BOWLING ---
    else:
        st.subheader(f"⚾ Bowling: {st.session_state.u_team} (Defending {st.session_state.target})")
        cpu_bat = st.session_state.c_roster[st.session_state.c_wickets]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("CPU Score", f"{st.session_state.c_score}/{st.session_state.c_wickets}")
        c2.metric("Target", st.session_state.target)
        c3.metric("Need", st.session_state.target - st.session_state.c_score)

        st.write(f"Bowling to: **{cpu_bat}**")

        if st.button("⚾ Deliver Ball"):
            u_dice, c_dice = random.randint(1, 6), random.randint(1, 6)
            st.write(f"Your Ball: {u_dice} | CPU Hit: {c_dice}")
            
            if u_dice == c_dice:
                st.success(f"WICKET! {cpu_bat} is out!")
                st.session_state.c_wickets += 1
            else:
                st.session_state.c_score += c_dice
            
            # End Game Logic
            if st.session_state.c_score >= st.session_state.target:
                st.session_state.winner = st.session_state.c_team
                st.session_state.step = "result"
            elif st.session_state.c_wickets >= 10:
                st.session_state.winner = st.session_state.u_team
                st.session_state.step = "result"
            st.rerun()

# SCREEN: FINAL RESULT
elif st.session_state.step == "result":
    st.title("📊 Match Summary")
    if st.session_state.winner == st.session_state.u_team:
        st.balloons()
        st.success(f"🎉 CONGRATULATIONS! {st.session_state.u_team} WON! 🎉")
    else:
        st.error(f"😔 {st.session_state.c_team} won the match.")
    
    st.write(f"**{st.session_state.u_team}**: {st.session_state.u_score}/{st.session_state.u_wickets}")
    st.write(f"**{st.session_state.c_team}**: {st.session_state.c_score}/{st.session_state.c_wickets}")
    
    if st.button("Back to Main Menu"):
        st.session_state.clear()
        st.rerun()