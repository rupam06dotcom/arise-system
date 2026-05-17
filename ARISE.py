import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import random
from datetime import date, datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="ARISE SYSTEM",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# DATABASE
# =========================================================
conn = sqlite3.connect("system_v4.db", check_same_thread=False)
c = conn.cursor()

# =========================================================
# DATABASE INIT
# =========================================================
def init_db():

    c.execute("""
    CREATE TABLE IF NOT EXISTS hunter(
        name TEXT,
        level INT,
        xp INT,
        hp INT,
        mp INT,
        max_hp INT,
        max_mp INT,
        rank TEXT,
        strength INT,
        vit INT,
        agi INT,
        intel INT,
        sen INT,
        stat_points INT,
        title TEXT,
        gold INT,
        streak INT,
        goal TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS quests(
        d TEXT,
        title TEXT,
        xp INT,
        done INT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS inventory(
        item TEXT,
        rarity TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        d TEXT,
        action TEXT,
        value REAL
    )
    """)

    conn.commit()

init_db()

# =========================================================
# FUTURISTIC THEME
# =========================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

html, body, .main {
    background: #020208;
    color: #e0f7ff;
    font-family: 'Orbitron', sans-serif;
}

.block-container {
    padding-top: 1rem;
}

.sys-card {
    background: rgba(0,229,255,0.05);
    border: 1px solid rgba(0,229,255,0.2);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 15px;
    animation: glow 2s infinite alternate;
}

@keyframes glow {
    from {
        box-shadow: 0 0 10px rgba(0,229,255,0.1);
    }
    to {
        box-shadow: 0 0 25px rgba(0,229,255,0.5);
    }
}

.sys-title {
    color: #00e5ff;
    text-shadow: 0 0 12px #00e5ff;
}

.rank-box {
    padding: 10px;
    border-radius: 14px;
    background: rgba(124,77,255,0.15);
    border: 1px solid #7c4dff;
    text-align: center;
}

.hp-bar,.mp-bar,.xp-bar {
    height: 18px;
    background: #0b1220;
    border-radius: 10px;
    overflow: hidden;
    border:1px solid #00e5ff30;
}

.hp-fill {
    height:100%;
    background: linear-gradient(90deg,#ff1744,#ff5252);
}

.mp-fill {
    height:100%;
    background: linear-gradient(90deg,#00e5ff,#2979ff);
}

.xp-fill {
    height:100%;
    background: linear-gradient(90deg,#00e5ff,#7c4dff);
}

.stButton > button {
    width: 100%;
    border-radius: 12px;
    background: #08111f;
    color: #00e5ff;
    border: 1px solid #00e5ff;
    padding: 12px;
    font-weight: bold;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #00e5ff;
    color: black;
    box-shadow: 0 0 15px #00e5ff;
}

[data-testid="stChatMessage"] {
    background: rgba(0,229,255,0.04);
    border:1px solid rgba(0,229,255,0.2);
    border-radius:14px;
    padding:10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def fetch(query, params=()):
    return pd.read_sql_query(query, conn, params=params)

def get_rank(level):

    if level >= 100:
        return "S"

    elif level >= 75:
        return "A"

    elif level >= 50:
        return "B"

    elif level >= 30:
        return "C"

    elif level >= 15:
        return "D"

    return "E"

def level_up_player(name, gained_xp):

    player = fetch(
        "SELECT level, xp FROM hunter WHERE name=?",
        (name,)
    ).iloc[0]

    level = int(player["level"])
    current_xp = int(player["xp"]) + gained_xp

    leveled_up = False

    while current_xp >= level * 100:

        current_xp -= level * 100
        level += 1
        leveled_up = True

        c.execute("""
        UPDATE hunter
        SET
            stat_points = stat_points + 5,
            gold = gold + 100,
            max_hp = max_hp + 20,
            max_mp = max_mp + 10,
            hp = max_hp + 20,
            mp = max_mp + 10
        WHERE name=?
        """, (name,))

    rank = get_rank(level)

    c.execute("""
    UPDATE hunter
    SET level=?,
        xp=?,
        rank=?
    WHERE name=?
    """, (level, current_xp, rank, name))

    conn.commit()

    return leveled_up, level

# =========================================================
# PLAYER LOAD
# =========================================================
hunter = fetch("SELECT * FROM hunter")

if hunter.empty:

    st.markdown(
        "<h1 class='sys-title' style='text-align:center;margin-top:15%'>[ SYSTEM AWAKENING ]</h1>",
        unsafe_allow_html=True
    )

    with st.form("awakening"):

        name = st.text_input("Hunter Name")
        goal = st.selectbox(
            "Choose Path",
            [
                "Strength Monarch",
                "Shadow Monarch",
                "Tank Monarch"
            ]
        )

        submit = st.form_submit_button("ARISE")

        if submit:

            c.execute("""
            INSERT INTO hunter VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                name,
                1,
                0,
                100,
                50,
                100,
                50,
                "E",
                10,
                10,
                10,
                10,
                10,
                0,
                "Weakest Hunter",
                100,
                0,
                goal
            ))

            conn.commit()
            st.success("SYSTEM INITIALIZED")
            st.rerun()

    st.stop()

# =========================================================
# PLAYER DATA
# =========================================================
player = fetch("SELECT * FROM hunter").iloc[0]

name = player["name"]
level = int(player["level"])
xp = int(player["xp"])
hp = int(player["hp"])
mp = int(player["mp"])
max_hp = int(player["max_hp"])
max_mp = int(player["max_mp"])

strength = int(player["strength"])
vit = int(player["vit"])
agi = int(player["agi"])
intel = int(player["intel"])
sen = int(player["sen"])

rank = player["rank"]
stat_points = int(player["stat_points"])
title = player["title"]
gold = int(player["gold"])
streak = int(player["streak"])
goal = player["goal"]

xp_need = level * 100
today = str(date.today())

# =========================================================
# DAILY QUESTS
# =========================================================
daily = fetch(
    "SELECT * FROM quests WHERE d=?",
    (today,)
)

if daily.empty:

    quests = [
        ("100 Pushups", 30),
        ("Drink 3L Water", 20),
        ("Protein Goal Complete", 25),
        ("30 Min Cardio", 35)
    ]

    for q, xr in quests:
        c.execute(
            "INSERT INTO quests VALUES (?,?,?,0)",
            (today, q, xr)
        )

    conn.commit()

# =========================================================
# HEADER
# =========================================================
xp_p = min(100, (xp / xp_need) * 100)
hp_p = (hp / max_hp) * 100
mp_p = (mp / max_mp) * 100

st.markdown(f"""
<div class='sys-card'>

<h1 class='sys-title'>ARISE SYSTEM</h1>

<h2>{name}</h2>

<div class='rank-box'>
RANK {rank} • LEVEL {level}
</div>

<br>

<p>HP {hp}/{max_hp}</p>
<div class='hp-bar'>
<div class='hp-fill' style='width:{hp_p}%'></div>
</div>

<br>

<p>MP {mp}/{max_mp}</p>
<div class='mp-bar'>
<div class='mp-fill' style='width:{mp_p}%'></div>
</div>

<br>

<p>XP {xp}/{xp_need}</p>
<div class='xp-bar'>
<div class='xp-fill' style='width:{xp_p}%'></div>
</div>

<br>

<p>
<b>TITLE:</b> {title}
|
<b>GOAL:</b> {goal}
|
<b>GOLD:</b> {gold}
|
<b>STREAK:</b> {streak}
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "STATUS",
    "QUESTS",
    "DUNGEON",
    "INVENTORY",
    "STATS",
    "SYSTEM AI"
])

# =========================================================
# STATUS
# =========================================================
with tab1:

    st.subheader("HUNTER STATS")

    fig = go.Figure(go.Scatterpolar(
        r=[strength, vit, agi, intel, sen],
        theta=["STR", "VIT", "AGI", "INT", "SEN"],
        fill='toself',
        line_color='#00e5ff'
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(f"Available Stat Points: {stat_points}")

    c1, c2, c3 = st.columns(3)

    if c1.button("+ STR") and stat_points > 0:
        c.execute("""
        UPDATE hunter
        SET strength=strength+1,
            stat_points=stat_points-1
        WHERE name=?
        """, (name,))
        conn.commit()
        st.rerun()

    if c2.button("+ AGI") and stat_points > 0:
        c.execute("""
        UPDATE hunter
        SET agi=agi+1,
            stat_points=stat_points-1
        WHERE name=?
        """, (name,))
        conn.commit()
        st.rerun()

    if c3.button("+ VIT") and stat_points > 0:
        c.execute("""
        UPDATE hunter
        SET vit=vit+1,
            stat_points=stat_points-1,
            max_hp=max_hp+10,
            hp=hp+10
        WHERE name=?
        """, (name,))
        conn.commit()
        st.rerun()

    if st.button("RECOVER HP / MP"):

        c.execute("""
        UPDATE hunter
        SET hp=max_hp,
            mp=max_mp
        WHERE name=?
        """, (name,))

        conn.commit()

        st.success("Recovery Complete")
        st.rerun()

# =========================================================
# QUESTS
# =========================================================
with tab2:

    st.subheader("DAILY QUESTS")

    qs = fetch(
        "SELECT rowid,* FROM quests WHERE d=?",
        (today,)
    )

    for _, q in qs.iterrows():

        st.markdown(f"### {q['title']}")

        if bool(q["done"]):

            st.success("COMPLETED")

        else:

            if st.button(
                f"CLAIM +{q['xp']} XP",
                key=f"q{q['rowid']}"
            ):

                c.execute(
                    "UPDATE quests SET done=1 WHERE rowid=?",
                    (int(q["rowid"]),)
                )

                leveled, lvl = level_up_player(
                    name,
                    int(q["xp"])
                )

                if leveled:
                    st.balloons()
                    st.success(
                        f"LEVEL UP! LEVEL {lvl}"
                    )

                conn.commit()
                st.rerun()

# =========================================================
# DUNGEON
# =========================================================
with tab3:

    st.subheader("DUNGEON GATE")

    enemies = [
        {"name":"Goblin","hp":30,"xp":20,"gold":15},
        {"name":"Wolf","hp":50,"xp":35,"gold":25},
        {"name":"Orc","hp":80,"xp":50,"gold":40},
        {"name":"Shadow Beast","hp":120,"xp":90,"gold":60},
        {"name":"Demon King","hp":300,"xp":250,"gold":200},
    ]

    if "enemy" not in st.session_state:

        st.session_state.enemy = random.choice(enemies)
        st.session_state.enemy_hp = st.session_state.enemy["hp"]

    enemy = st.session_state.enemy

    st.markdown(f"""
    <div class='sys-card'>

    <h2>{enemy['name']}</h2>

    <p>HP: {st.session_state.enemy_hp}</p>

    <p>
    Reward:
    {enemy['xp']} XP /
    {enemy['gold']} GOLD
    </p>

    </div>
    """, unsafe_allow_html=True)

    if st.button("ATTACK"):

        dmg = random.randint(
            5,
            max(5, strength * 2)
        )

        st.session_state.enemy_hp -= dmg

        st.success(
            f"You dealt {dmg} damage!"
        )

        enemy_damage = random.randint(5, 20)

        c.execute("""
        UPDATE hunter
        SET hp = hp - ?
        WHERE name=?
        """, (enemy_damage, name))

        conn.commit()

        st.warning(
            f"{enemy['name']} dealt {enemy_damage} damage!"
        )

        updated = fetch(
            "SELECT hp FROM hunter WHERE name=?",
            (name,)
        ).iloc[0]

        if int(updated["hp"]) <= 0:

            c.execute("""
            UPDATE hunter
            SET hp=max_hp,
                mp=max_mp,
                gold=max(gold-50,0)
            WHERE name=?
            """, (name,))

            conn.commit()

            st.error("YOU DIED IN THE DUNGEON")

            st.session_state.enemy = random.choice(enemies)
            st.session_state.enemy_hp = st.session_state.enemy["hp"]

            st.rerun()

        if st.session_state.enemy_hp <= 0:

            c.execute("""
            UPDATE hunter
            SET gold=gold+?
            WHERE name=?
            """, (
                enemy["gold"],
                name
            ))

            conn.commit()

            leveled, lvl = level_up_player(
                name,
                enemy["xp"]
            )

            if leveled:

                st.balloons()

                st.success(
                    f"LEVEL UP! LEVEL {lvl}"
                )

            st.success(
                f"{enemy['name']} Defeated!"
            )

            loot = random.choice([
                "Common",
                "Rare",
                "Epic"
            ])

            c.execute("""
            INSERT INTO inventory VALUES (?,?)
            """, (
                f"{enemy['name']} Core",
                loot
            ))

            shadow_chance = random.randint(1, 100)

            if shadow_chance <= 25:

                shadow_name = f"Shadow {enemy['name']}"

                c.execute("""
                INSERT INTO inventory VALUES (?,?)
                """, (
                    shadow_name,
                    "Shadow Soldier"
                ))

                st.success(
                    f"SHADOW EXTRACTED: {shadow_name}"
                )

            conn.commit()

            st.session_state.enemy = random.choice(enemies)
            st.session_state.enemy_hp = st.session_state.enemy["hp"]

        st.rerun()

# =========================================================
# INVENTORY
# =========================================================
with tab4:

    st.subheader("INVENTORY")

    inv = fetch(
        "SELECT * FROM inventory"
    )

    if inv.empty:

        st.info("Inventory Empty")

    else:

        st.dataframe(
            inv,
            use_container_width=True
        )

# =========================================================
# STATS
# =========================================================
with tab5:

    st.subheader("PLAYER ANALYTICS")

    chart = go.Figure(go.Bar(
        x=["STR","VIT","AGI","INT","SEN"],
        y=[strength, vit, agi, intel, sen]
    ))

    chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=400
    )

    st.plotly_chart(
        chart,
        use_container_width=True
    )

# =========================================================
# SYSTEM AI
# =========================================================
with tab6:

    st.subheader("SYSTEM ASSISTANT")

    st.caption(
        "Ask about stats, quests, dungeons, or training."
    )

    if "messages" not in st.session_state:

        st.session_state.messages = [
            {
                "role":"assistant",
                "content":
                f"""
Welcome Hunter {name}.

Rank:
{rank}

Level:
{level}

XP:
{xp}/{xp_need}

The System is ready.
"""
            }
        ]

    for m in st.session_state.messages:

        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input(
        "Speak to the System..."
    ):

        st.session_state.messages.append(
            {
                "role":"user",
                "content":prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        low = prompt.lower()

        if "quest" in low:

            reply = "Complete all daily quests to maximize XP gain."

        elif "level" in low or "xp" in low:

            reply = f"""
You are Level {level}.

Current XP:
{xp}/{xp_need}

Need:
{xp_need - xp} XP
to level up.
"""

        elif "stat" in low:

            reply = f"""
STR: {strength}
VIT: {vit}
AGI: {agi}
INT: {intel}
SEN: {sen}

Unused Points:
{stat_points}
"""

        elif "dungeon" in low:

            reply = f"""
Current Enemy:
{st.session_state.enemy['name']}

Enemy HP:
{st.session_state.enemy_hp}
"""

        elif "diet" in low:

            reply = """
High protein.
Enough water.
Good sleep.
Consistent calories.
"""

        else:

            reply = random.choice([
                "Arise.",
                "Every rep is XP.",
                "The System is watching.",
                "Keep growing, Hunter."
            ])

        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.messages.append(
            {
                "role":"assistant",
                "content":reply
            }
        )

# =========================================================
# FOOTER
# =========================================================
st.caption(
    f"Last Updated: {datetime.now().strftime('%d %B %Y • %I:%M %p')}"
        )
