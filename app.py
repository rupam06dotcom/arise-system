import os
import binascii
import hashlib
from datetime import date

import streamlit as st
import psycopg2
import psycopg2.extras


st.set_page_config(page_title="ARISE", page_icon="⚔️", layout="wide")


# ---------- DB ----------
def get_conn():
    return psycopg2.connect(st.secrets["DATABASE_URL"], sslmode="require")


def fetch_one(query, params=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchone()


def fetch_all(query, params=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchall()


def execute(query, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
        conn.commit()


# ---------- Auth ----------
def hash_pw(password, salt=None):
    salt = salt or binascii.hexlify(os.urandom(16)).decode()
    pwdhash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    return salt, binascii.hexlify(pwdhash).decode()


def verify_pw(password, salt, pwdhash):
    _, new_hash = hash_pw(password, salt)
    return new_hash == pwdhash


def signup(email, password, name):
    email = email.strip().lower()
    name = name.strip()

    if not email or not password or not name:
        return None

    salt, pwdhash = hash_pw(password)

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO users (email, password_salt, password_hash)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id
                    """,
                    (email, salt, pwdhash),
                )
                user = cur.fetchone()
                if not user:
                    conn.rollback()
                    return None

                uid = user["id"]
                cur.execute(
                    "INSERT INTO profiles (user_id, name) VALUES (%s, %s)",
                    (uid, name),
                )
                conn.commit()
                return uid
            except Exception:
                conn.rollback()
                raise


def login(email, password):
    email = email.strip().lower()
    user = fetch_one(
        """
        SELECT id, password_salt, password_hash
        FROM users
        WHERE email=%s AND is_active=TRUE
        """,
        (email,),
    )
    if user and verify_pw(password, user["password_salt"], user["password_hash"]):
        execute("UPDATE users SET last_login=NOW() WHERE id=%s", (user["id"],))
        return user["id"]
    return None


# ---------- Helpers ----------
def get_profile(uid):
    return fetch_one("SELECT * FROM profiles WHERE user_id=%s", (uid,))


def add_xp(uid, amount):
    prof = get_profile(uid)
    if not prof:
        return

    new_xp = int(prof["xp"]) + int(amount)
    new_level = int(prof["level"])

    while new_xp >= new_level * 100:
        new_xp -= new_level * 100
        new_level += 1

    execute(
        "UPDATE profiles SET xp=%s, level=%s, updated_at=NOW() WHERE user_id=%s",
        (new_xp, new_level, uid),
    )


def xp_progress(prof):
    return f"{prof['xp']}/{prof['level'] * 100}"


# ---------- Session ----------
if "uid" not in st.session_state:
    st.session_state.uid = None


# ---------- Auth UI ----------
if not st.session_state.uid:
    st.title("⚔️ ARISE - Solo Leveling System")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        pw = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            uid = login(email, pw)
            if uid:
                st.session_state.uid = uid
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("New Email", key="signup_email")
        name = st.text_input("Hunter Name", key="signup_name")
        pw = st.text_input("New Password", type="password", key="signup_pw")
        if st.button("Create Account"):
            try:
                uid = signup(email, pw, name)
                if uid:
                    st.success("Account created. Login now.")
                else:
                    st.error("Email already exists or fields are empty")
            except Exception as e:
                st.error(f"Signup failed: {e}")

    st.stop()


# ---------- Main App ----------
uid = st.session_state.uid
prof = get_profile(uid)

if not prof:
    st.error("Profile not found.")
    st.stop()

st.sidebar.title(prof["title"])
st.sidebar.metric("Level", prof["level"])
st.sidebar.metric("XP", xp_progress(prof))
st.sidebar.metric("Rank", prof["rank"])
st.sidebar.metric("Gold", prof["gold"])

if st.sidebar.button("Logout"):
    st.session_state.uid = None
    st.rerun()

st.header(f"Welcome back, {prof['name']}!")

col1, col2, col3 = st.columns(3)
col1.metric("HP", f"{prof['hp']}/{prof['max_hp']}")
col2.metric("MP", f"{prof['mp']}/{prof['max_mp']}")
col3.metric("Streak", prof["streak"])

today = date.today()

# ---------- Daily Quests ----------
st.subheader("Daily Quests")

quests = fetch_all(
    """
    SELECT *
    FROM quests
    WHERE user_id=%s AND quest_date=%s
    ORDER BY id
    """,
    (uid, today),
)

for qst in quests:
    done = qst["status"] == "completed"
    checked = st.checkbox(
        f"{qst['title']} (+{qst['xp']} XP)",
        value=done,
        key=f"q_{qst['id']}",
        disabled=done,
    )

    if checked and not done:
        execute(
            """
            UPDATE quests
            SET status='completed', completed_at=NOW(), updated_at=NOW()
            WHERE id=%s
            """,
            (qst["id"],),
        )
        add_xp(uid, qst["xp"])
        execute(
            "INSERT INTO logs (user_id, d, action, value) VALUES (%s, %s, %s, %s)",
            (uid, today, "quest_complete", qst["xp"]),
        )
        st.rerun()

if st.button("Generate Today's Quests"):
    existing = fetch_one(
        "SELECT 1 FROM quests WHERE user_id=%s AND quest_date=%s LIMIT 1",
        (uid, today),
    )
    if not existing:
        defaults = [
            ("Push-ups 30", 20),
            ("Read 10 pages", 15),
            ("Meditate 5 min", 10),
        ]
        with get_conn() as conn:
            with conn.cursor() as cur:
                for title, xp in defaults:
                    cur.execute(
                        """
                        INSERT INTO quests (user_id, quest_date, title, xp, status)
                        VALUES (%s, %s, %s, %s, 'active')
                        """,
                        (uid, today, title, xp),
                    )
            conn.commit()
        st.rerun()
    else:
        st.info("Today's quests already exist.")

# ---------- Workout ----------
st.subheader("Workout Session")

mode = st.selectbox("Mode", ["Strength", "Cardio", "Mixed"])

if st.button("Start 25-min Session"):
    execute(
        """
        INSERT INTO workout_sessions
        (user_id, session_date, title, mode, start_time, status)
        VALUES (%s, %s, %s, %s, NOW(), 'active')
        """,
        (uid, today, f"{mode} Training", mode),
    )
    st.success("Session started!")

active = fetch_one(
    """
    SELECT *
    FROM workout_sessions
    WHERE user_id=%s AND status='active'
    ORDER BY start_time DESC
    LIMIT 1
    """,
    (uid,),
)

if active:
    if st.button("Complete Session"):
        elapsed = 25
        xp_reward = 30

        execute(
            """
            UPDATE workout_sessions
            SET end_time=NOW(),
                elapsed_minutes=%s,
                xp_reward=%s,
                status='completed',
                updated_at=NOW()
            WHERE id=%s
            """,
            (elapsed, xp_reward, active["id"]),
        )

        add_xp(uid, xp_reward)
        execute(
            "UPDATE profiles SET gold=gold+%s, updated_at=NOW() WHERE user_id=%s",
            (10, uid),
        )
        execute(
            "INSERT INTO logs (user_id, d, action, value) VALUES (%s, %s, %s, %s)",
            (uid, today, "workout_complete", xp_reward),
        )

        st.success(f"+{xp_reward} XP, +10 Gold!")
        st.rerun()

# ---------- Inventory ----------
st.subheader("Inventory")

items = fetch_all(
    """
    SELECT item, rarity, obtained_at
    FROM inventory
    WHERE user_id=%s
    ORDER BY obtained_at DESC
    LIMIT 10
    """,
    (uid,),
)

if items:
    for it in items:
        st.write(f"• {it['item']} — *{it['rarity']}*")
else:
    st.caption("No items yet.")

st.caption("Data is stored in PostgreSQL.")
