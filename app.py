import streamlit as st
import asyncio
import edge_tts
import base64
import os
import re
import time
from mutagen.mp3 import MP3 # 音声の長さを測るためのライブラリ

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
    ssml_text = text.replace("/", ",")
    communicate = edge_tts.Communicate(text=ssml_text, voice="en-US-GuyNeural", rate=speed)
    await communicate.save("speech.mp3")
    # 音声の長さを取得（秒単位）
    audio = MP3("speech.mp3")
    return audio.info.length

def get_audio_html(file_path, key):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        # keyを付与することで、ブラウザに別の音声として認識させ、強制再生させる
        return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}" id="audio_{key}">'

# --- 3. UI設定 & カスタムCSS ---
st.set_page_config(page_title="English Road Trip", layout="wide")

# CSSの更新（Repeat!ボタンを目立たせる）
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
        color: #EF4444 !important;
        font-weight: bold;
        margin: 0 5px;
    }
    .ja-text {
        font-size: 20px !important;
        color: #059669 !important;
        font-weight: 500;
        background-color: #ECFDF5;
        padding: 5px 10px;
        border-radius: 5px;
    }
    /* ボタンのスタイル調整 */
    .stButton > button {
        border-radius: 20px;
        font-weight: bold;
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

# --- 4. 教材セット ---
with st.expander("📝 教材をセットする", expanded=True):
    input_text = st.text_area("English Text (Use / for chunks)", height=150)
    input_ja = st.text_area("Japanese Translation", height=100)

if not input_text:
    st.info("英文を貼り付けて修行を開始しましょう！")
    st.stop()

def format_slash(text):
    return text.replace("/", '<span class="slash">/</span>')

sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', input_text) if s.strip()]
ja_sentences = [j.strip() for j in re.split(r'(?<=[。！？\n])', input_ja) if j.strip()]

# --- 5. 修行ステップ ---
st.divider()
tabs = st.tabs(["R0: Intro", "R1: Repeat (x2)", "R2: Interpret", "R3: Overlap", "R4: Shadow", "R5: Performance"])

# --- R1: Repeat (x2) ---
with tabs[1]:
    st.subheader("Round 1: Double Repeating")
    st.write("ボタンを押すと音声が2回流れます。1回目で聞き取り、2回目で重ねて発音しましょう。")
    for i, s in enumerate(sentences):
        st.markdown(f'<p class="en-text">{i+1}. {format_slash(s)}</p>', unsafe_allow_html=True)
        if st.button(f"🔁 Repeat!", key=f"r1_{i}"):
            with st.spinner("Preparing voice..."):
                duration = asyncio.run(generate_voice(s))
            
            # 1回目の再生
            st.markdown(get_audio_html("speech.mp3", f"1st_{i}"), unsafe_allow_html=True)
            
            # 音声の長さ + 0.8秒のポーズを待機
            time.sleep(duration + 0.8)
            
            # 2回目の再生
            st.markdown(get_audio_html("speech.mp3", f"2nd_{i}"), unsafe_allow_html=True)
        st.write("---")

# --- R2: Interpret ---
with tabs[2]:
    st.subheader("Round 2: Interpretation")
    for i, s in enumerate(sentences):
        with st.container(border=True):
            st.markdown(f'<p class="en-text">{format_slash(s)}</p>', unsafe_allow_html=True)
            if i < len(ja_sentences):
                st.markdown(f'<p class="ja-text">意味: {ja_sentences[i]}</p>', unsafe_allow_html=True)
            if st.button(f"🔊 Repeat!", key=f"r2_{i}"):
                asyncio.run(generate_voice(s))
                st.markdown(get_audio_html("speech.mp3", f"r2_{i}"), unsafe_allow_html=True)

# ※ R0, R3, R4, R5 の各ボタン名も "Repeat!" または "Start" に統一して実装（コード量削減のため中略、構造は前回同様）
# 他のタブも同様に、音声再生部分を get_audio_html("speech.mp3", key) に置き換えてください。
