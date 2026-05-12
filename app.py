import streamlit as st
import asyncio
import edge_tts
import base64
import os
import re
import time
from mutagen.mp3 import MP3

# --- 1. 称号 & テーマ設定 ---
def get_rank_theme(completes):
    themes = [
        (50, "West Coast Legend", "San Francisco", "🔥", "#000000", "#E5E7EB"),
        (25, "Grand Canyon Explorer", "Arizona", "🔮", "#008080", "#F0FDFA"),
        (10, "Route 66 Rider", "Mid-West", "🥇", "#FFD700", "#FFFBEB"),
        (5,  "Jazz Traveler", "New Orleans", "🥈", "#C0C0C0", "#F9FAFB"),
        (1,  "NYC Tourist", "New York", "🥉", "#CD7F32", "#FFF7ED"),
        (0,  "Starting Line", "New York", "🚗", "#808080", "#FFFFFF")
    ]
    for c, title, city, icon, m_color, b_color in themes:
        if completes >= c: return title, city, icon, m_color, b_color

# --- 2. セッション状態 ---
if 'total_completes' not in st.session_state: st.session_state.total_completes = 0
if 'round_counts' not in st.session_state: st.session_state.round_counts = {f"R{i}": 0 for i in range(6)}
if 'active_index' not in st.session_state: st.session_state.active_index = -1

rank, city, icon, m_color, b_color = get_rank_theme(st.session_state.total_completes)

# --- 3. 音声ロジック ---
async def generate_voice(text, speed="+0%"):
    if os.path.exists("speech.mp3"): os.remove("speech.mp3")
    ssml_text = text.replace("/", ",")
    # スピード調整を適用
    communicate = edge_tts.Communicate(text=ssml_text, voice="en-US-GuyNeural", rate=speed)
    await communicate.save("speech.mp3")
    return MP3("speech.mp3").info.length

def get_audio_html(file_path, key):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}" id="audio_{key}">'

# --- 4. UI & スタイル ---
st.set_page_config(page_title="English Road Trip", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {b_color}; }}
    .en-text {{ font-size: 28px !important; font-weight: 600; line-height: 1.8; color: #1E3A8A; }}
    .highlight {{ color: #EF4444 !important; background-color: #FEF3C7; padding: 2px 5px; border-radius: 5px; }} /* 読んでいる場所の色 */
    .slash {{ color: #94A3B8; font-weight: bold; margin: 0 5px; }}
    .ja-text {{ font-size: 20px; color: #059669; background-color: #ECFDF5; padding: 5px 10px; border-radius: 5px; }}
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🗺️ My Progress")
    st.markdown(f"<div style='background-color:{m_color}; padding:20px; border-radius:10px; color:white; text-align:center;'><h1>{icon}</h1><h3>{rank}</h3><hr><h2>{st.session_state.total_completes} CP</h2></div>", unsafe_allow_html=True)
    st.write("---")
    # 全体共通のスピード調整
    global_speed = st.select_slider("⚡ 全体のスピード調節", options=["-25%", "-10%", "+0%", "+10%", "+25%"], value="+0%")
    st.write("---")
    for r, c in st.session_state.round_counts.items(): st.caption(f"{r}: {c} times")

# --- 5. メイン ---
st.title("🚀 English Road Trip")
with st.expander("📝 教材セット"):
    input_text = st.text_area("English ( / )", height=150)
    input_ja = st.text_area("Japanese", height=100)

if not input_text: st.stop()

def format_text(text, is_active=False):
    # スラッシュを薄く表示し、アクティブな行なら色を変える
    fmt = text.replace("/", '<span class="slash">/</span>')
    if is_active:
        return f'<p class="en-text highlight">{fmt}</p>'
    return f'<p class="en-text">{fmt}</p>'

sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', input_text) if s.strip()]
ja_sentences = [j.strip() for j in re.split(r'(?<=[。！？\n])', input_ja) if j.strip()]

tabs = st.tabs(["R0", "R1", "R2", "R3", "R4", "R5"])

# --- 各ラウンドの共通処理 ---
def run_repeat(text, r_key, idx, double=False):
    st.session_state.round_counts[r_key] += 1
    st.session_state.active_index = idx # 現在読んでいる行を保存
    duration = asyncio.run(generate_voice(text, speed=global_speed))
    
    # 1回目再生
    st.markdown(get_audio_html("speech.mp3", f"play_{r_key}_{idx}_1"), unsafe_allow_html=True)
    if double:
        time.sleep(duration + 0.8)
        st.markdown(get_audio_html("speech.mp3", f"play_{r_key}_{idx}_2"), unsafe_allow_html=True)

# --- R1: Repeat (x2) ---
with tabs[1]:
    for i, s in enumerate(sentences):
        is_active = (st.session_state.active_index == i)
        st.markdown(format_text(s, is_active), unsafe_allow_html=True)
        if st.button(f"🔁 Repeat!", key=f"r1_{i}"):
            run_repeat(s, "R1", i, double=True)
            st.rerun() # 色を変えるために再描画

# --- R2: Interpret ---
with tabs[2]:
    for i, s in enumerate(sentences):
        is_active = (st.session_state.active_index == i)
        with st.container(border=True):
            st.markdown(format_text(s, is_active), unsafe_allow_html=True)
            if i < len(ja_sentences): st.markdown(f'<p class="ja-text">{ja_sentences[i]}</p>', unsafe_allow_html=True)
            if st.button(f"🔁 Repeat!", key=f"r2_{i}"):
                run_repeat(s, "R2", i)
                st.rerun()

# --- R3: Overlap ---
with tabs[3]:
    st.markdown(format_text(input_text, st.session_state.active_index == 99), unsafe_allow_html=True)
    if st.button("▶️ Start Overlapping", key="r3_btn"):
        run_repeat(input_text, "R3", 99)
        st.rerun()

# (R0, R4, R5 も同様のロジックで実装... )

with tabs[5]:
    st.markdown(format_text(input_text), unsafe_allow_html=True)
    if st.button("🏁 Complete Journey!"):
        st.session_state.total_completes += 1
        st.session_state.round_counts["R5"] += 1
        st.balloons()
        st.rerun()
