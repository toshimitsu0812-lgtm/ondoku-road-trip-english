import streamlit as st
import asyncio
import edge_tts
import base64
import os
import re

# --- 1. 称号システム ---
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

# --- 2. 音声生成・再生ロジック ---
async def generate_voice(text, speed="+0%"):
    if os.path.exists("speech.mp3"):
        os.remove("speech.mp3")
    # スラッシュをコンマに置換することで、AI音声に自然なポーズ（タメ）を作らせる
    ssml_text = text.replace("/", ",")
    communicate = edge_tts.Communicate(ssml_text, "en-US-GuyNeural", rate=speed)
    await communicate.save("speech.mp3")

def play_audio():
    if os.path.exists("speech.mp3"):
        with open("speech.mp3", "rb") as f:
            st.audio(f.read(), format="audio/mp3")

# --- 3. UI設定 & カスタムCSS ---
st.set_page_config(page_title="English Road Trip", layout="wide")

st.markdown("""
    <style>
    .en-text {
        font-size: 28px !important;
        font-weight: 600 !important;
        line-height: 1.8 !important;
        color: #1E3A8A !important;
        margin-bottom: 10px;
    }
    .slash {
        color: #EF4444 !important; /* スラッシュを赤色にして目立たせる */
        font-weight: bold;
        margin: 0 5px;
    }
    .ja-text {
        font-size: 18px !important;
        color: #4B5563 !important;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🗺️ My Progress")
    user_name = st.text_input("Name", "Student")
    total_comp = st.number_input("Total Completes", 0, step=1)
    rank, city, icon, color = get_rank(total_comp)
    st.markdown(f"<div style='background-color:{color}; padding:20px; border-radius:10px; color:white; text-align:center;'><h2>{icon} {rank}</h2><p>{city}</p></div>", unsafe_allow_html=True)

st.title("🚀 English Road Trip")

# --- 4. テキスト入力エリア ---
with st.expander("📝 教材をセットする（スラッシュ / を入れてください）", expanded=True):
    st.caption("例: I have a dream / that one day / this nation will rise up.")
    input_text = st.text_area("English Text", placeholder="英文を入力...", height=150)
    input_ja = st.text_area("Japanese Translation", placeholder="和訳を入力...", height=100)

if not input_text:
    st.info("英文にスラッシュを入れて貼り付けてください！")
    st.stop()

# スラッシュを赤色で表示するためのヘルパー関数
def format_slash(text):
    return text.replace("/", '<span class="slash">/</span>')

# テキストを一文ごとに分割
sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', input_text) if s.strip()]
ja_sentences = [j.strip() for j in re.split(r'(?<=[。！？]) +', input_ja) if j.strip()]

# --- 5. 修行ステップ ---
st.divider()
tabs = st.tabs(["R0: Intro", "R1: Repeat", "R2: Interpret", "R3: Overlap", "R4: Shadow", "R5: Performance"])

# --- R0: 意味確認 ---
with tabs[0]:
    st.subheader("Round 0: Orientation")
    st.markdown(f'<p class="en-text">{format_slash(input_text)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="ja-text">{input_ja}</p>', unsafe_allow_html=True)
    st.audio_input("音読を記録 (R0)")

# --- R1: 一文ごとのリピーティング ---
with tabs[1]:
    st.subheader("Round 1: Sentence Repeating")
    for i, s in enumerate(sentences):
        st.markdown(f'<p class="en-text">{i+1}. {format_slash(s)}</p>', unsafe_allow_html=True)
        if st.button(f"🔊 Listen {i+1}", key=f"r1_{i}"):
            asyncio.run(generate_voice(s))
            play_audio()
        st.write("---")

# --- R2: 意味を確認してリピーティング ---
with tabs[2]:
    st.subheader("Round 2: Interpretation & Repeat")
    for i, s in enumerate(sentences):
        with st.container(border=True):
            st.markdown(f'<p class="en-text">{format_slash(s)}</p>', unsafe_allow_html=True)
            if i < len(ja_sentences):
                st.markdown(f'<p class="ja-text">意味: {ja_sentences[i]}</p>', unsafe_allow_html=True)
            if st.button(f"🔊 Listen {i+1}", key=f"r2_{i}"):
                asyncio.run(generate_voice(s))
                play_audio()

# --- R3: オーバーラッピング ---
with tabs[3]:
    st.subheader("Round 3: Overlapping")
    speed_option = st.select_slider("再生スピード", options=["-20%", "-10%", "+0%", "+10%", "+20%"], value="+0%", key="r3_s")
    st.markdown(f'<p class="en-text">{format_slash(input_text)}</p>', unsafe_allow_html=True)
    if st.button("▶️ Start Overlapping"):
        asyncio.run(generate_voice(input_text, speed=speed_option))
        play_audio()

# --- R4: シャドーイング（文字なし） ---
with tabs[4]:
    st.subheader("Round 4: Shadowing")
    st.warning("耳に集中してください！")
    speed_shadow = st.select_slider("再生スピード", options=["-20%", "-10%", "+0%", "+10%", "+20%"], value="+0%", key="r4_s")
    if st.button("▶️ Start Shadowing"):
        asyncio.run(generate_voice(input_text, speed=speed_shadow))
        play_audio()

# --- R5: 本番音読 ---
with tabs[5]:
    st.subheader("Round 5: Final Performance")
    # R5はスラッシュなしで実力を試すのもアリですが、今回は指示通りスラッシュありで表示します
    st.markdown(f'<p class="en-text">{format_slash(input_text)}</p>', unsafe_allow_html=True)
    st.audio_input("魂の音読を録音")
    if st.button("🏁 Journey Complete!"):
        st.balloons()
