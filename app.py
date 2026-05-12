import streamlit as st
import asyncio
import edge_tts
import base64
import os
import re
import time
from mutagen.mp3 import MP3

# --- 1. 称号システム & 背景色設定 ---
def get_rank_theme(completes):
    # (しきい値, 称号, 都市, アイコン, メイン色, 背景色)
    themes = [
        (50, "West Coast Legend", "San Francisco", "🔥", "#000000", "#E5E7EB"),
        (25, "Grand Canyon Explorer", "Arizona", "🔮", "#008080", "#F0FDFA"),
        (10, "Route 66 Rider", "Mid-West", "🥇", "#FFD700", "#FFFBEB"),
        (5,  "Jazz Traveler", "New Orleans", "🥈", "#C0C0C0", "#F9FAFB"),
        (1,  "NYC Tourist", "New York", "🥉", "#CD7F32", "#FFF7ED"),
        (0,  "Starting Line", "New York", "🚗", "#808080", "#FFFFFF")
    ]
    for c, title, city, icon, m_color, b_color in themes:
        if completes >= c:
            return title, city, icon, m_color, b_color

# --- 2. セッション状態の初期化 (リロードしてもカウントを保持) ---
if 'total_completes' not in st.session_state:
    st.session_state.total_completes = 0
if 'round_counts' not in st.session_state:
    st.session_state.round_counts = {f"R{i}": 0 for i in range(6)}

# 現在のテーマ取得
rank, city, icon, m_color, b_color = get_rank_theme(st.session_state.total_completes)

# --- 3. 音声エンジン ---
async def generate_voice(text, speed="+0%"):
    if os.path.exists("speech.mp3"): os.remove("speech.mp3")
    ssml_text = text.replace("/", ",")
    communicate = edge_tts.Communicate(text=ssml_text, voice="en-US-GuyNeural", rate=speed)
    await communicate.save("speech.mp3")
    return MP3("speech.mp3").info.length

def get_audio_html(file_path, key):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}" id="audio_{key}">'

# --- 4. UI設定 & 動的CSS ---
st.set_page_config(page_title="English Road Trip", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {b_color}; /* ランクで背景色が変わる */
    }}
    .en-text {{
        font-size: 28px !important;
        font-weight: 600 !important;
        line-height: 1.8 !important;
        color: #1E3A8A !important;
    }}
    .slash {{ color: #EF4444 !important; font-weight: bold; margin: 0 5px; }}
    .ja-text {{ font-size: 20px !important; color: #059669 !important; background-color: #ECFDF5; padding: 5px 10px; border-radius: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# サイドバー (操作不可のステータス画面)
with st.sidebar:
    st.title("🗺️ My Progress")
    st.write(f"**Player:** {rank}")
    
    # ステータスカード
    st.markdown(f"""
    <div style='background-color:{m_color}; padding:20px; border-radius:10px; color:white; text-align:center;'>
        <h1 style='margin:0;'>{icon}</h1>
        <h3 style='margin:0;'>{rank}</h3>
        <p style='margin:0;'>Next: {city}</p>
        <hr>
        <h2 style='margin:0;'>{st.session_state.total_completes} CP</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.write("**Round Breakdown**")
    for r_name, count in st.session_state.round_counts.items():
        st.write(f"{r_name}: {count} times")

# --- 5. メイン教材 ---
st.title("🚀 English Road Trip")

with st.expander("📝 教材をセット"):
    input_text = st.text_area("English (Use / )", height=150)
    input_ja = st.text_area("Japanese", height=100)

if not input_text:
    st.stop()

sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', input_text) if s.strip()]
ja_sentences = [j.strip() for j in re.split(r'(?<=[。！？\n])', input_ja) if j.strip()]

tabs = st.tabs(["R0", "R1", "R2", "R3", "R4", "R5"])

# 各ラウンドの処理（共通ロジック：ボタンを押すと round_counts が増える）
def record_round(r_key):
    st.session_state.round_counts[r_key] += 1

# --- 例として R1 のみ詳細記述 (他も同様に record_round を呼ぶ) ---
with tabs[1]:
    st.subheader("Round 1: Double Repeating")
    for i, s in enumerate(sentences):
        st.markdown(f'<p class="en-text">{i+1}. {s.replace("/", "/")}</p>', unsafe_allow_html=True)
        if st.button(f"🔁 Repeat!", key=f"r1_{i}"):
            record_round("R1") # カウントアップ
            duration = asyncio.run(generate_voice(s))
            st.markdown(get_audio_html("speech.mp3", f"1st_{i}"), unsafe_allow_html=True)
            time.sleep(duration + 0.8)
            st.markdown(get_audio_html("speech.mp3", f"2nd_{i}"), unsafe_allow_html=True)

# --- R5: ゴール判定 ---
with tabs[5]:
    st.subheader("Round 5: Performance")
    st.markdown(f'<p class="en-text">{input_text}</p>', unsafe_allow_html=True)
    if st.button("🏁 Complete Journey!"):
        st.session_state.total_completes += 1
        record_round("R5")
        st.balloons()
        st.rerun() # 背景色を即座に反映させるために再起動
