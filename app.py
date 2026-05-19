import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="ARISE SYSTEM", page_icon="⚔️", layout="centered")

# --- SUPABASE ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- STYLES (Solo Leveling theme) ---
st.markdown("""
<style>
   .main { background: #0a0a0f; color: #e0e0ff; }
   .stButton>button { background: linear-gradient(90deg,#6a00ff,#00d4ff); color:white; border:none; border-radius:8px; font-weight:bold; }
    h1, h2, h3 { color:#a855f7; text-shadow:0 0 10px #6a00ff; }
</style>
""", unsafe_allow_html=True)

# --- AUTH POPUP ---
@st.dialog("SYSTEM GATE", width="large")
def login_gate():
    st.markdown("<h2 style='text-align:center'>⚔️ ARISE ⚔️</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>Only the chosen Hunter may enter</p>", unsafe_allow_html=True)

    login_tab, signup_tab = st.tabs(["LOGIN", "AWAKEN"])

    with login_tab:
        email = st.text_input("Email", placeholder="hunter@email.com")
        pw = st.text_input("Password", type="password")
        if st.button("ENTER", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.email = email
                st.rerun()
            except:
                st.error("Access Denied")

    with signup_tab:
        email = st.text_input("Email", key="s_email")
        pw = st.text_input("Password", type="password", key="s_pw")
        name = st.text_input("Hunter Name", placeholder="RUPAM")
        if st.button("AWAKEN NOW", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": email, "password": pw})
                # create hunter
                supabase.table("hunters").insert({
                    "email": email,
                    "hunter_name": name.upper(),
                    "level": 1, "xp": 0, "hp": 100, "max_hp": 100,
                    "mp": 50, "max_mp": 50, "strength": 10,
                    "agility": 10, "intelligence": 10, "gold": 100,
                    "rank": "E", "title": "The Weakest Hunter"
                }).execute()
                st.success("Awakening Successful! Go to LOGIN tab.")
            except Exception as e:
                st.error(f"Failed: {e}")

# --- CHECK AUTH ---
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    login_gate()
    st.stop()

# --- LOAD HUNTER ---
email = st.session_state.email
hunter_res = supabase.table("hunters").select("*").eq("email", email).execute()
if not hunter_res.data:
    st.error("Hunter data not found. Contact admin.")
    st.stop()

hunter = hunter_res.data[0]

# --- HEADER ---
st.markdown(f"<h1>ARISE SYSTEM</h1>", unsafe_allow_html=True)
st.markdown(f"### Hunter: {hunter['hunter_name']} | Rank: {hunter['rank']}")

col1, col2, col3 = st.columns(3)
col1.metric("LEVEL", hunter['level'])
col2.metric("XP", f"{hunter['xp']}/100")
col3.metric("GOLD", hunter['gold'])

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 STATUS", "📜 QUESTS", "👥 SHADOW ARMY"])

with tab1:
    st.subheader("STATS")
    c1, c2, c3 = st.columns(3)
    c1.metric("HP", f"{hunter['hp']}/{hunter['max_hp']}")
    c2.metric("MP", f"{hunter['mp']}/{hunter['max_mp']}")
    c3.metric("TITLE", hunter['title'])

    st.progress(hunter['xp'] % 100 / 100)

    st.subheader("Attributes")
    st.write(f"**STR:** {hunter['strength']} | **AGI:** {hunter['agility']} | **INT:** {hunter['intelligence']}")

    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.rerun()

with tab2:
    st.subheader("Daily Quest")
    if st.button("Complete Daily Training (+50 XP)", use_container_width=True):
        new_xp = hunter['xp'] + 50
        new_level = hunter['level']
        if new_xp >= 100:
            new_level += 1
            new_xp -= 100
            st.balloons()
            st.success(f"LEVEL UP! You are now Level {new_level}")

        supabase.table("hunters").update({
            "xp": new_xp, "level": new_level, "gold": hunter['gold'] + 20
        }).eq("email", email).execute()

        # log quest
        supabase.table("quests").insert({
            "hunter_id": hunter['id'],
            "title": "Daily Training",
            "xp_reward": 50,
            "completed": True
        }).execute()

        time.sleep(1)
        st.rerun()

with tab3:
    st.subheader("Shadow Army")
    shadows = supabase.table("shadow_army").select("*").eq("hunter_id", hunter['id']).execute()
    if shadows.data:
        for s in shadows.data:
            st.write(f"• {s['shadow_name']} - Rank {s['shadow_rank']}")
    else:
        st.info("No shadows yet. Arise a defeated enemy to add them.")
