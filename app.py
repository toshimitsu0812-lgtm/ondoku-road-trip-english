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
# 利用可能な声のリスト
VOICE_OPTIONS = {
    "Guy (Male)": "en-US-GuyNeural",
    "Aria (Female)": "en-US-AriaNeural",
    "Christopher (Male)": "en-US-ChristopherNeural",
    "Jenny (Female)": "en-US-JennyNeural",
    "Eric (Male)": "en-GB-RyanNeural"
}

async def generate_voice(text, voice_id, speed="+0%"):
    if os.path.exists("speech.mp3"):
        try: os.remove("speech.mp3")
        except: pass
    ssml_text = text.replace("/", ",")
    communicate = edge_tts.Communicate(text=ssml_text, voice=voice_id, rate=speed)
    await communicate.save("speech.mp3")
    return MP3("speech.mp3").info.length

def get_audio_html(file_path, key):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        # 再生後にHTML要素を消去しないよう、一意のIDを付与
        return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}" id="audio_{key}_{time.time()}">'

# --- 4. UI & スタイル ---
st.set_page_config(page_title="English Road Trip", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {b_color}; }}
    .en-text {{ font-size: 28px !important; font-weight: 600; line-height: 1.8; color: #1E3A8A; }}
    .highlight {{ color: #EF4444 !important; background-color: #FEF3C7; padding: 5px; border-radius: 5px; }}
    .slash {{ color: #94A3B8; font-weight: bold; margin: 0 5px; }}
    .ja-text {{ font-size: 20px !important; color: #059669 !important; background-color: #ECFDF5; padding: 10px 15px; border-radius: 8px; line-height: 1.5; display: block; width: 100%; }}
    .goal-box {{ background-color: #F3F4F6; border-left: 5px solid #3B82F6; padding: 10px 15px; margin-bottom: 20px; font-size: 16px; color: #1F2937; }}
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🗺️ My Progress")
    st.markdown(f"<div style='background-color:{m_color}; padding:20px; border-radius:10px; color:white; text-align:center;'><h1>{icon}</h1><h3>{rank}</h3><hr><h2>{st.session_state.total_completes} CP</h2></div>", unsafe_allow_html=True)
    st.write("---")
    
    # 声の選択
    selected_voice_name = st.selectbox("🎙️ ボイス選択", list(VOICE_OPTIONS.keys()))
    target_voice = VOICE_OPTIONS[selected_voice_name]
    
    # スピード調整
    global_speed = st.select_slider("⚡ スピード調節", options=["-25%", "-10%", "+0%", "+10%", "+25%"], value="+0%")
    st.write("---")
    for r, c in st.session_state.round_counts.items(): st.caption(f"{r}: {c} times")

# --- 5. メイン ---
st.title("🚀 English Road Trip")
with st.expander("📝 教材セット"):
    input_text = st.text_area("English ( / )", height=150)
    input_ja = st.text_area("Japanese", height=100)

if not input_text: st.stop()

def format_text(text, is_active=False):
    fmt = text.replace("/", '<span class="slash">/</span>')
    if is_active: return f'<p class="en-text highlight">{fmt}</p>'
    return f'<p class="en-text">{fmt}</p>'

sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', input_text) if s.strip()]
ja_sentences = [j.strip() for j in re.split(r'(?<=[。！？\n])', input_ja) if j.strip()]

tabs = st.tabs(["R0: Intro", "R1: Repeat", "R2: Interpret", "R3: Overlap", "R4: Shadow", "R5: Performance"])

ROUND_GOALS = {
    0: "【目標】意味を確認し、一度自力で音読する。",
    1: "【目標】モデルをよく聞き、一文ずつ正確に2回リピートする。",
    2: "【目標】意味を頭に浮かべながら、感情を込めて一文ずつリピートする。",
    3: "【目標】モデル音声と同時に発音し、リズムを体に染み込ませる。",
    4: "【目標】文字を見ずに音声だけを頼りに追いかける。",
    5: "【目標】聞き手を意識して、堂々と最終パフォーマンス！"
}

for i, tab in enumerate(tabs):
    with tab:
        st.markdown(f'<div class="goal-box">{ROUND_GOALS[i]}</div>', unsafe_allow_html=True)
        
        if i == 0:
            st.markdown(format_text(input_text), unsafe_allow_html=True)
            st.markdown(f'<div class="ja-text">{input_ja}</div>', unsafe_allow_html=True)
            
        elif i == 1:
            for j, s in enumerate(sentences):
                active = (st.session_state.active_index == j)
                st.markdown(format_text(s, active), unsafe_allow_html=True)
                if st.button(f"🔁 Repeat!", key=f"r1_{j}"):
                    st.session_state.round_counts["R1"] += 1
                    st.session_state.active_index = j
                    duration = asyncio.run(generate_voice(s, target_voice, speed=global_speed))
                    st.markdown(get_audio_html("speech.mp3", f"r1_{j}_1"), unsafe_allow_html=True)
                    time.sleep(duration + 0.8)
                    st.markdown(get_audio_html("speech.mp3", f"r1_{j}_2"), unsafe_allow_html=True)
                    st.rerun()

        elif i == 2:
            for j, s in enumerate(sentences):
                active = (st.session_state.active_index == j)
                st.markdown(format_text(s, active), unsafe_allow_html=True)
                if j < len(ja_sentences): st.markdown(f'<div class="ja-text">{ja_sentences[j]}</div>', unsafe_allow_html=True)
                if st.button(f"🔁 Speak!", key=f"r2_{j}"):
                    st.session_state.round_counts["R2"] += 1
                    st.session_state.active_index = j
                    asyncio.run(generate_voice(s, target_voice, speed=global_speed))
                    st.markdown(get_audio_html("speech.mp3", f"r2_{j}"), unsafe_allow_html=True)
                    st.rerun()

        elif i == 3:
            st.markdown(format_text(input_text, st.session_state.active_index == 99), unsafe_allow_html=True)
            if st.button("▶️ Start Overlapping", key="r3_btn"):
                st.session_state.round_counts["R3"] += 1
                st.session_state.active_index = 99
                asyncio.run(generate_voice(input_text, target_voice, speed=global_speed))
                st.markdown(get_audio_html("speech.mp3", "r3"), unsafe_allow_html=True)
                st.rerun()

        elif i == 4:
            st.warning("Concentrate on the Sound!")
            if st.button("▶️ Start Shadowing", key="r4_btn"):
                st.session_state.round_counts["R4"] += 1
                asyncio.run(generate_voice(input_text, target_voice, speed=global_speed))
                st.markdown(get_audio_html("speech.mp3", "r4"), unsafe_allow_html=True)

        elif i == 5:
            st.markdown(format_text(input_text), unsafe_allow_html=True)
            if st.button("🏁 Complete Journey!"):
                st.session_state.total_completes += 1
                st.session_state.round_counts["R5"] += 1
                st.balloons()
                st.rerun()
