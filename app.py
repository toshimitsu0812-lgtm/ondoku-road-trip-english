import streamlit as st
import asyncio
import edge_tts
import base64
import os

# --- 1. 教材データ（ここを自由に書き換えてください） ---
# 複数の教材を入れたい場合は、辞書形式で増やせます
MATERIALS = {
    "L1": {
        "title": "I Have a Dream",
        "en": "I have a dream that one day this nation will rise up and live out the true meaning of its creed.",
        "ja": "私には夢がある。いつの日か、この国が立ち上がり、その信条の真の意味を実践することを。"
    },
    "L2": {
        "title": "Imagine",
        "en": "Imagine all the people living life in peace. You may say I'm a dreamer, but I'm not the only one.",
        "ja": "すべての人が平和に生きていると想像してごらん。君は僕を夢想家だと言うかもしれない。でも、僕一人じゃないんだ。"
    }
}

# --- 2. 称号システム (Road Trip) ---
def get_rank(completes):
    ranks = [
        (50, "West Coast Legend", "San Francisco", "🔥", "#000000"),
        (25, "Grand Canyon Explorer", "Arizona", "🔮", "#008080"),
        (10, "Route 66 Rider", "Mid-West", "🥇", "#FFD700"),
        (5,  "Jazz Traveler", "New Orleans", "🥈", "#C0C0C0"),
        (1,  "NYC Tourist", "New York", "🥉", "#CD7F32"),
        (0,  "Starting Line", "New York", "🚗", "#808080")
    ]
    for c, title, city, icon, color in ranks:
        if completes >= c:
            return title, city, icon, color

# --- 3. 音声生成ロジック ---
async def generate_voice(text):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save("speech.mp3")

# --- 4. メインUI ---
st.set_page_config(page_title="English Road Trip", layout="wide")

# URLの末尾 (?lesson=L1) から教材を特定。指定がなければL1を表示。
query_params = st.query_params
lesson_id = query_params.get("lesson", "L1")

# 教材の取得
lesson_data = MATERIALS.get(lesson_id, MATERIALS["L1"])

# サイドバー (進捗表示)
with st.sidebar:
    st.title("🗺️ My Progress")
    user_name = st.text_input("Name", "Student")
    total_comp = st.number_input("Total Completes", 0, step=1)
    rank, city, icon, color = get_rank(total_comp)
    st.markdown(f"<div style='background-color:{color}; padding:20px; border-radius:10px; color:white; text-align:center;'><h2>{icon} {rank}</h2><p>Dest: {city}</p></div>", unsafe_allow_html=True)

# メインコンテンツ
st.title(f"🚀 {lesson_data['title']}")

tab0, tab1, tab2 = st.tabs(["📖 Reading", "🎧 Training", "🏁 Finish"])

with tab0:
    st.subheader("Text & Meaning")
    st.info(lesson_data['en'])
    with st.expander("日本語訳を表示"):
        st.write(lesson_data['ja'])

with tab1:
    mode = st.radio("Practice Mode", ["Visible (R1-R3)", "Hidden (R4)"])
    if mode == "Visible (R1-R3)":
        st.info(lesson_data['en'])
    else:
        st.warning("Concentrate on the SOUND!")
    
    if st.button("🔊 Play Voice"):
        asyncio.run(generate_voice(lesson_data['en']))
        with open("speech.mp3", "rb") as f:
            st.audio(f.read(), format="audio/mp3")

with tab2:
    st.subheader("Goal!")
    if st.button("Complete Journey"):
        st.balloons()
        st.success(f"Well done, {user_name}! You've made progress toward {city}!")
