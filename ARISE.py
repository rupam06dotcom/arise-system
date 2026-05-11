import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import date

st.set_page_config(page_title="ARISE", page_icon="🔷", layout="wide", initial_sidebar_state="collapsed")
conn = sqlite3.connect("system.db", check_same_thread=False)
c = conn.cursor()

# --- SOLO LEVELING THEME ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&display=swap');
html, body,.main {background:#020208; color:#e0f7ff}
h1,h2,h3 {font-family:'Orbitron',sans-serif}
.sys-card {background:rgba(0,229,255,0.06); border:1px solid rgba(0,229,255,0.25); border-radius:18px; padding:16px}
.sys-title {color:#00e5ff; text-shadow:0 0 12px #00e5ff}
.xp-bar {height:12px; background:#0b1220; border-radius:10px; overflow:hidden; border:1px solid #00e5ff50}
.xp-fill {height:100%; background:linear-gradient(90deg,#00e5ff,#7c4dff)}
.stButton>button {background:#0a1629; color:#00e5ff; border:1px solid #00e5ff; border-radius:12px; font-family:'Orbitron'}
.stButton>button:hover {background:#00e5ff; color:#000}
</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
def init():
    c.execute("CREATE TABLE IF NOT EXISTS hunter(name TEXT, level INT, xp INT, rank TEXT, str INT, vit INT, agi INT, intel INT, sen INT, goal TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS quests(d TEXT, title TEXT, type TEXT, target INT, prog INT, xp INT, done INT)")
    c.execute("CREATE TABLE IF NOT EXISTS logs(d TEXT, kind TEXT, val REAL)")
    conn.commit()
init()

h = pd.read_sql("SELECT * FROM hunter", conn)
if h.empty:
    st.markdown("<h1 class='sys-title' style='text-align:center;margin-top:20%'>[SYSTEM INITIALIZING]</h1>", unsafe_allow_html=True)
    with st.form("awakening"):
        name = st.text_input("Hunter Name", "Rupam")
        goal = st.selectbox("Choose Path", ["Strength Monarch","Shadow Monarch (Cut)","Tank Monarch (Bulk)"])
        if st.form_submit_button("AWAKEN"):
            # FIXED: now 10 values for 10 columns
            c.execute("INSERT INTO hunter VALUES (?,?,?,?,?,?,?,?,?,?)", (name, 1, 0, "E", 10, 10, 10, 10, 10, goal))
            conn.commit()
            st.rerun()
    st.stop()

name, level, xp, rank, STR, VIT, AGI, INT, SEN, goal = h.iloc[0]
xp_need = level * 100
today = str(date.today())

# --- DAILY QUESTS ---
if pd.read_sql("SELECT * FROM quests WHERE d=?", conn, params=(today,)).empty:
    for title, target, xp_r in [("Daily: 50 Push-ups", 50, 20), ("Daily: Protein", 1, 15), ("Daily: 3L Water", 3, 10)]:
        c.execute("INSERT INTO quests VALUES (?,?,?,?,?,?,0)", (today, title, "daily", target, 0, xp_r))
    conn.commit()

# --- HEADER ---
st.markdown(f"""
<div class='sys-card'>
  <h2 class='sys-title'>PLAYER: {name}</h2>
  <p>RANK {rank} • Lv.{level}</p>
  <div class='xp-bar'><div class='xp-fill' style='width:{min(100, xp/xp_need*100)}%'></div></div>
  <p>{xp}/{xp_need} XP</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["STATUS","QUESTS","DUNGEON"])

with tab1:
    fig = go.Figure(go.Scatterpolar(r=[STR,VIT,AGI,INT,SEN], theta=["STR","VIT","AGI","INT","SEN"], fill='toself', line_color='#00e5ff'))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=300, showlegend=False, font_color="white")
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"**Path:** {goal}")

with tab2:
    qs = pd.read_sql("SELECT rowid,* FROM quests WHERE d=?", conn, params=(today,))
    for _, q in qs.iterrows():
        st.write(f"**{q.title}**")
        if st.button(f"CLAIM +{q.xp} XP", key=f"q{q.rowid}", disabled=q.done):
            c.execute("UPDATE quests SET done=1 WHERE rowid=?", (q.rowid,))
            new_xp = xp + q.xp
            if new_xp >= xp_need:
                c.execute("UPDATE hunter SET level=level+1, xp=?, str=str+2 WHERE rowid=1", (new_xp - xp_need,))
                st.balloons()
            else:
                c.execute("UPDATE hunter SET xp=? WHERE rowid=1", (new_xp,))
            conn.commit()
            st.rerun()

with tab3:
    st.markdown("<h3 class='sys-title'>[DUNGEON GATE]</h3>", unsafe_allow_html=True)
    if st.button("ENTER E-RANK GATE"):
        c.execute("UPDATE hunter SET xp=xp+50, str=str+1")
        c.execute("INSERT INTO logs VALUES (?,?,?)", (today, "workout", 1))
        conn.commit()
        st.success("GATE CLEARED! +50 XP")
        st.rerun()