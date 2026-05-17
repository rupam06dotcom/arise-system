# =========================================================
# ARISE SYSTEM v4.3 - AD FREE EDITION (based on v3)
# =========================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import random
from datetime import date, datetime, timedelta

st.set_page_config(page_title="ARISE SYSTEM", page_icon="🔷", layout="wide", initial_sidebar_state="expanded")

# PWA Setup
st.markdown("""
<link rel="manifest" href="app/static/manifest.json">
<meta name="theme-color" content="#00d4ff">
<script>if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('app/static/service-worker.js'));}</script>
""", unsafe_allow_html=True)

conn = sqlite3.connect("system_v3.db", check_same_thread=False)
c = conn.cursor()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');
html, body, .main {background:#020208;color:#e0f7ff;font-family:'Orbitron',sans-serif;}
.block-container{padding-top:1rem;}
.sys-card{background:rgba(0,229,255,0.05);border:1px solid rgba(0,229,255,0.2);border-radius:20px;padding:20px;margin-bottom:15px;box-shadow:0 0 15px rgba(0,229,255,0.08);animation:pulseGlow 3s infinite;}
@keyframes pulseGlow{0%{box-shadow:0 0 5px #00e5ff;}50%{box-shadow:0 0 20px #00e5ff;}100%{box-shadow:0 0 5px #00e5ff;}}
.sys-title{color:#00e5ff;text-shadow:0 0 12px #00e5ff;}
.rank-box{padding:10px;border-radius:14px;background:rgba(124,77,255,0.15);border:1px solid #7c4dff;text-align:center;}
.hp-bar,.mp-bar,.xp-bar{height:18px;background:#0b1220;border-radius:10px;overflow:hidden;border:1px solid #00e5ff30;}
.hp-fill{height:100%;background:linear-gradient(90deg,#ff1744,#ff5252);}
.mp-fill{height:100%;background:linear-gradient(90deg,#00e5ff,#2979ff);}
.xp-fill{height:100%;background:linear-gradient(90deg,#00e5ff,#7c4dff);}
.stButton>button{width:100%;border-radius:12px;background:#08111f;color:#00e5ff;border:1px solid #00e5ff;padding:12px;font-weight:bold;transition:0.2s;}
.stButton>button:hover{background:#00e5ff;color:black;box-shadow:0 0 15px #00e5ff;}
</style>
""", unsafe_allow_html=True)

def init_db():
    c.execute("""CREATE TABLE IF NOT EXISTS hunter(name TEXT,level INT,xp INT,hp INT,mp INT,max_hp INT,max_mp INT,rank TEXT,strength INT,vit INT,agi INT,intel INT,sen INT,stat_points INT,title TEXT,gold INT,streak INT,goal TEXT,last_active TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS quests(d TEXT,title TEXT,xp INT,gold INT,done INT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS inventory(item TEXT,rarity TEXT)""")
    conn.commit()
init_db()

def get_rank(level):
    return "S" if level>=100 else "A" if level>=75 else "B" if level>=50 else "C" if level>=30 else "D" if level>=15 else "E"

def apply_xp_gain(current_xp, current_level, gained_xp):
    new_xp=current_xp+gained_xp; new_level=current_level; levels_gained=0
    while new_xp>=new_level*100:
        new_xp-=new_level*100; new_level+=1; levels_gained+=1
    return new_xp,new_level,levels_gained

hunter=pd.read_sql_query("SELECT * FROM hunter",conn)
if hunter.empty:
    st.markdown("<h1 class='sys-title' style='text-align:center;margin-top:10%'>[ SYSTEM AWAKENING v4.3 ]</h1>",unsafe_allow_html=True)
    with st.form("awaken"):
        name=st.text_input("Hunter Name")
        path=st.selectbox("Choose Path",["Strength Monarch","Shadow Monarch","Balanced Monarch"])
        submit=st.form_submit_button("ARISE")
        if submit and name.strip():
            goal="Muscle Gain" if "Strength" in path else "Fat Loss" if "Shadow" in path else "Recomp"
            c.execute("INSERT INTO hunter VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(name.strip(),1,0,100,50,100,50,"E",10,10,10,10,10,0,"Weakest Hunter",100,0,goal,str(date.today())))
            conn.commit(); st.success("SYSTEM INITIALIZED - AD FREE"); st.rerun()
    st.stop()

player=pd.read_sql_query("SELECT * FROM hunter",conn).iloc[0]
name,level,xp,hp,mp,max_hp,max_mp = player["name"],int(player["level"]),int(player["xp"]),int(player["hp"]),int(player["mp"]),int(player["max_hp"]),int(player["max_mp"])
strength,vit,agi,intel,sen = int(player["strength"]),int(player["vit"]),int(player["agi"]),int(player["intel"]),int(player["sen"])
rank,stat_points,title,gold,streak,goal = get_rank(level),int(player["stat_points"]),player["title"],int(player["gold"]),int(player["streak"]),player["goal"]
last_active=player.get("last_active",str(date.today()))
xp_need=level*100; today=str(date.today())

if last_active!=today:
    yesterday=str(date.today()-timedelta(days=1))
    streak=streak+1 if last_active==yesterday else 1
    c.execute("UPDATE hunter SET streak=?,last_active=?",(streak,today)); conn.commit()

daily=pd.read_sql_query("SELECT * FROM quests WHERE d=?",conn,params=(today,))
if daily.empty:
    for q in [("100 Pushups",30,40),("Drink 3L Water",20,20),("Protein Goal Complete",25,30),("30 Min Cardio",35,50)]:
        c.execute("INSERT INTO quests VALUES (?,?,?,?,?)",(today,q[0],q[1],q[2],0))
    conn.commit()
qs=pd.read_sql_query("SELECT rowid,* FROM quests WHERE d=?",conn,params=(today,))

xp_p=min(100,(xp/xp_need)*100); hp_p=(hp/max_hp)*100; mp_p=(mp/max_mp)*100
st.markdown(f"""<div class='sys-card'><h1 class='sys-title'>ARISE SYSTEM v4.3</h1><h2>{name}</h2><div class='rank-box'>RANK {rank} • LEVEL {level} • AD-FREE</div><br><p>HP {hp}/{max_hp}</p><div class='hp-bar'><div class='hp-fill' style='width:{hp_p:.1f}%'></div></div><br><p>MP {mp}/{max_mp}</p><div class='mp-bar'><div class='mp-fill' style='width:{mp_p:.1f}%'></div></div><br><p>XP {xp}/{xp_need}</p><div class='xp-bar'><div class='xp-fill' style='width:{xp_p:.1f}%'></div></div><br><p><b>TITLE:</b> {title} | <b>GOAL:</b> {goal} | <b>GOLD:</b> {gold} | <b>STREAK:</b> {streak} DAYS</p></div>""",unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(["STATUS","QUESTS","DUNGEON","INVENTORY","STATS","SYSTEM AI"])

with tab1:
    st.subheader("HUNTER STATS")
    fig=go.Figure(go.Scatterpolar(r=[strength,vit,agi,intel,sen],theta=["STR","VIT","AGI","INT","SEN"],fill='toself',line_color='#00e5ff'))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="white",height=450); st.plotly_chart(fig,use_container_width=True)
    st.write(f"Available Stat Points: **{stat_points}**")
    c1,c2,c3=st.columns(3); c4,c5=st.columns(2)
    if c1.button("+ STR") and stat_points>0: c.execute("UPDATE hunter SET strength=strength+1,stat_points=stat_points-1"); conn.commit(); st.rerun()
    if c2.button("+ AGI") and stat_points>0: c.execute("UPDATE hunter SET agi=agi+1,stat_points=stat_points-1"); conn.commit(); st.rerun()
    if c3.button("+ VIT") and stat_points>0: c.execute("UPDATE hunter SET vit=vit+1,stat_points=stat_points-1,max_hp=max_hp+10"); conn.commit(); st.rerun()
    if c4.button("+ INT") and stat_points>0: c.execute("UPDATE hunter SET intel=intel+1,stat_points=stat_points-1,max_mp=max_mp+5"); conn.commit(); st.rerun()
    if c5.button("+ SEN") and stat_points>0: c.execute("UPDATE hunter SET sen=sen+1,stat_points=stat_points-1"); conn.commit(); st.rerun()

with tab2:
    st.subheader("DAILY QUESTS")
    for _,q in qs.iterrows():
        col_a,col_b=st.columns([3,1]); col_a.markdown(f"### {q['title']}"); col_b.markdown(f"**+{q['xp']} XP / +{q['gold']} GOLD**")
        if st.button("CLAIM REWARD",key=f"q{q['rowid']}",disabled=bool(q['done'])):
            c.execute("UPDATE quests SET done=1 WHERE rowid=?",(q['rowid'],)); new_xp,new_level,levels_gained=apply_xp_gain(xp,level,int(q['xp'])); stat_bonus=levels_gained*5; new_rank=get_rank(new_level)
            c.execute("UPDATE hunter SET level=?,xp=?,stat_points=stat_points+?,gold=gold+?,rank=?",(new_level,new_xp,stat_bonus,int(q['gold']),new_rank)); conn.commit()
            if levels_gained: st.balloons(); st.success(f"LEVEL UP! Now Level {new_level} - Rank {new_rank}!")
            else: st.success("QUEST COMPLETED"); st.rerun()
    done_count=int(qs['done'].sum()); st.info(f"Progress: {done_count}/{len(qs)} quests | Streak: {streak} days")

with tab3:
    st.subheader("DUNGEON GATE")
    enemies=[{"name":"Goblin","hp":30,"xp":20,"gold":15},{"name":"Wolf","hp":50,"xp":35,"gold":25},{"name":"Orc","hp":80,"xp":50,"gold":40},{"name":"Shadow Beast","hp":120,"xp":90,"gold":60}]
    if "enemy" not in st.session_state: st.session_state.enemy=random.choice(enemies); st.session_state.enemy_hp=st.session_state.enemy["hp"]
    enemy=st.session_state.enemy; st.markdown(f"<div class='sys-card'><h2>{enemy['name']}</h2><p>HP: {st.session_state.enemy_hp}/{enemy['hp']}</p><p>Reward: {enemy['xp']} XP | {enemy['gold']} GOLD</p></div>",unsafe_allow_html=True)
    st.write(f"Your MP: **{mp}/{max_mp}**")
    if st.button("ATTACK"):
        if mp<5: st.warning("Not enough MP!")
        else:
            dmg=random.randint(5,max(6,strength*2)); new_mp=max(0,mp-5); st.session_state.enemy_hp-=dmg; c.execute("UPDATE hunter SET mp=?",(new_mp,)); conn.commit(); st.success(f"You dealt {dmg} damage!")
            if st.session_state.enemy_hp<=0:
                new_xp,new_level,levels_gained=apply_xp_gain(xp,level,enemy["xp"]); c.execute("UPDATE hunter SET xp=?,level=?,gold=gold+?,stat_points=stat_points+?,rank=?,mp=?",(new_xp,new_level,enemy["gold"],levels_gained*5,get_rank(new_level),min(max_mp,new_mp+20))); conn.commit(); st.balloons(); st.success(f"{enemy['name']} Defeated!"); st.session_state.enemy=random.choice(enemies); st.session_state.enemy_hp=st.session_state.enemy["hp"]
            st.rerun()
    if st.button("REST"): restored=min(max_mp,mp+30); c.execute("UPDATE hunter SET mp=?",(restored,)); conn.commit(); st.success(f"MP restored"); st.rerun()

with tab4:
    st.subheader("INVENTORY"); inv=pd.read_sql_query("SELECT * FROM inventory",conn); st.info("Defeat enemies to earn loot!") if inv.empty else [st.markdown(f"**[{r['rarity']}]** {r['item']}") for _,r in inv.iterrows()]

with tab5:
    st.subheader("PLAYER ANALYTICS"); chart=go.Figure(go.Bar(x=["STR","VIT","AGI","INT","SEN"],y=[strength,vit,agi,intel,sen],marker_color=["#ff5252","#00e5ff","#69ff47","#7c4dff","#ffd740"])); chart.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="white",height=400); st.plotly_chart(chart,use_container_width=True)

with tab6:
    st.subheader("SYSTEM ASSISTANT v4.3"); st.info("Ad-Free Update Active - Your progress is saved locally")
