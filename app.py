import streamlit as st
import sqlite3
import datetime

DB = "arise.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS quests (u TEXT, d TEXT, q1 INT, q2 INT, q3 INT, q4 INT, q5 INT, PRIMARY KEY(u,d))""")
    conn.commit()
    conn.close()

def verify_user(u,p):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE u=? AND p=?", (u,p)); r = c.fetchone(); conn.close(); return r is not None

def create_user(u,p):
    try:
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?,?)", (u,p)); conn.commit(); conn.close(); return True
    except: return False

def get_q(u,d):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT q1,q2,q3,q4,q5 FROM quests WHERE u=? AND d=?", (u,d)); r = c.fetchone(); conn.close()
    return r if r else (0,0,0,0,0)

def save_q(u,d,v):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("REPLACE INTO quests VALUES (?,?,?,?,?,?,?)", (u,d,*v)); conn.commit(); conn.close()

init_db()

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');
.stApp {{
    background-image: url("https://raw.githubusercontent.com/rupam06dotcom/arise-system/main/IMG_20260520_093149.png");
    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
    background-repeat: no-repeat;
    font-family: 'Outfit', sans-serif;
}}
.block-container {{ padding-top: 0rem !important; max-width: 430px; }}
header {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

/* liquid glass card - lil curve */
.glass {{
    background: rgba(12, 12, 20, 0.52);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 22px;
    padding: 26px 22px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    margin-top: 58vh;
}}

/* inputs */
div[data-testid="stTextInput"] > div > div > input {{
    background: rgba(0,0,0,0.38) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important;
    color: #e6e6e6 !important;
    padding: 14px 14px 14px 44px !important;
    font-size: 15px !important;
}}
div[data-testid="stTextInput"]:first-of-type > div > div > input {{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23888' viewBox='0 0 24 24'%3E%3Cpath d='M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v3h20v-3c0-3.3-6.7-5-10-5z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: 14px center;
    background-size: 18px;
}}
div[data-testid="stTextInput"]:nth-of-type(2) > div > div > input {{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23888' viewBox='0 0 24 24'%3E%3Cpath d='M18 8h-1V6c0-2.8-2.2-5-5-5S7 3.2 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.7 1.4-3.1 3.1-3.1 1.7 0 3.1 1.4 3.1 3.1v2z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: 14px center;
    background-size: 18px;
}}

/* login button */
div.stButton > button:first-child {{
    background: linear-gradient(135deg, #5b21b6, #7c3aed 60%, #9333ea);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px;
    font-weight: 700;
    letter-spacing: 2px;
    width: 100%;
    margin-top: 8px;
    box-shadow: 0 0 22px rgba(124,58,237,0.45), inset 0 0 10px rgba(255,255,255,0.1);
    transition: transform .15s;
}}
div.stButton > button:first-child:hover {{ transform: translateY(-1px); }}

.forgot {{ text-align: right; color: #a78bfa; font-size: 13px; margin: 8px 4px 18px; }}

.or {{ display:flex; align-items:center; color:#777; font-size:12px; margin:18px 0; }}
.or::before, .or::after {{ content:''; flex:1; height:1px; background:rgba(255,255,255,0.12); }}
.or span {{ padding:0 12px; }}

.google-btn {{
    background: rgba(0,0,0,0.38);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 12px;
    text-align: center;
    color: #ddd;
    display:flex; align-items:center; justify-content:center; gap:10px;
}}

/* dashboard */
.dashboard {{ margin-top: 12vh; }}
.xp-wrap {{
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    height: 14px;
    overflow: hidden;
    margin: 12px 0 20px;
}}
.xp-fill {{
    height: 100%;
    background: linear-gradient(90deg, #7c3aed, #a855f7, #c084fc);
    box-shadow: 0 0 12px rgba(168,85,247,0.7);
    transition: width .4s ease;
    border-radius: 12px;
}}
h2.player {{ color:white; margin:0 0 6px; font-weight:700; letter-spacing:1px; }}
p.sub {{ color:#a1a1aa; margin:0 0 14px; font-size:13px; }}
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state: st.session_state.user = None
QUESTS = ["100 Push-ups","100 Sit-ups","100 Squats","10KM Run","No Excuses"]

if not st.session_state.user:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    u = st.text_input("", placeholder="Email or Username", key="lu", label_visibility="collapsed")
    p = st.text_input("", placeholder="Password", type="password", key="lp", label_visibility="collapsed")
    st.markdown('<div class="forgot">Forgot Password?</div>', unsafe_allow_html=True)
    login = st.button("LOGIN")
    st.markdown('<div class="or"><span>OR</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="google-btn"><img src="https://www.svgrepo.com/show/475656/google-color.svg" width="18"> Continue with Google</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#888; font-size:12px; margin-top:14px;">New here? <span style="color:#a78bfa">Create account below</span></div>', unsafe_allow_html=True)
    nu = st.text_input("", placeholder="New Hunter ID", key="nu", label_visibility="collapsed")
    np = st.text_input("", placeholder="New Password", type="password", key="np", label_visibility="collapsed")
    create = st.button("AWAKEN")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if login:
        if verify_user(u,p): st.session_state.user = u; st.rerun()
        else: st.error("Invalid credentials")
    if create:
        if nu and np:
            if create_user(nu,np): st.success("Hunter registered. Login now.")
            else: st.error("ID exists")
else:
    today = datetime.date.today().isoformat()
    qvals = list(get_q(st.session_state.user, today))
    completed = sum(qvals)
    percent = int(completed / len(QUESTS) * 100)
    
    st.markdown('<div class="glass dashboard">', unsafe_allow_html=True)
    st.markdown(f'<h2 class="player">HUNTER: {st.session_state.user.upper()}</h2>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub">XP Progress â€¢ {completed}/5 Complete</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="xp-wrap"><div class="xp-fill" style="width:{percent}%"></div></div>', unsafe_allow_html=True)
    
    new_vals = []
    for i,q in enumerate(QUESTS):
        checked = st.checkbox(q, value=bool(qvals[i]), key=f"q{i}")
        new_vals.append(1 if checked else 0)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("SAVE"): save_q(st.session_state.user, today, new_vals); st.toast("Progress saved", icon="âš”ï¸")
    with col2:
        if st.button("LOGOUT"): st.session_state.user = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
