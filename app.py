import streamlit as st
import asyncio
import edge_tts
import base64
import os
import re
import time

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
    # スラッシュをコンマに置換してポーズを作る
    ssml_text = text.replace("/", ",")
    communicate = edge_tts.Communicate(ssml_text, "en-US-GuyNeural", rate=speed)
    await communicate.save("speech.mp3")

def get_audio_html(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'

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
        color: #EF4444 !important;
        font-weight: bold;
        margin: 0 5px;
    }
    .ja-text {
        font-size: 20px !important;
        color: #059669 !important; /* 和訳を緑系にして区別 */
        font-weight: 500;
        background-color: #ECFDF5;
        padding: 5px 10px;
        border-radius: 5px;
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
with st.expander("📝 教材をセットする", expanded=True):
    input_text = st.text_area("English Text (Use / for chunks)", placeholder="英文を入力...", height=150)
    input_ja = st.text_area("Japanese Translation (Separate with Enter or punctuation)", placeholder="和訳を入力...", height=100)

if not input_text:
    st.info("英文を貼り付けて修行を開始しましょう！")
    st.stop()

# ヘルパー関数
def format_slash(text):
    return text.replace("/", '<span class="slash">/</span>')

# 文の分割（英文と和訳）
sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', input_text) if s.strip()]
# 和訳は改行または句読点で分割
ja_sentences = [j.strip() for j in re.split(r'(?<=[。！？\n])', input_ja) if j.strip()]

# --- 5. 修行ステップ ---
st.divider()
tabs = st.tabs(["R0: Intro", "R1: Repeat (x2)", "R2: Interpret", "R3: Overlap", "R4: Shadow", "R5: Performance"])

# --- R0: Intro ---
with tabs[0]:
    st.subheader("Round 0: Orientation")
    st.markdown(f'<p class="en-text">{format_slash(input_text)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:18px; color:gray;">{input_ja}</p>', unsafe_allow_html=True)
    st.audio_input("音読を記録 (R0)")

# --- R1: Repeat (2回流れる) ---
with tabs[1]:
    st.subheader("Round 1: Double Listening")
    st.write("ボタンを押すと音声が2回流れます。2回目に合わせて、または後に続いてリピート！")
    for i, s in enumerate(sentences):
        st.markdown(f'<p class="en-text">{i+1}. {format_slash(s)}</p>', unsafe_allow_html=True)
        if st.button(f"🔊 Listen (x2)", key=f"r1_{i}"):
            asyncio.run(generate_voice(s))
            # 1回目
            st.markdown(get_audio_html("speech.mp3"), unsafe_allow_html=True)
            time.sleep(1.5) # 1.5秒のポーズ
            # 2回目（ブラウザの仕様上、同じタグだと再生されない場合があるため少し工夫）
            st.markdown(get_audio_html("speech.mp3").replace("audio/mp3", "audio/mpeg"), unsafe_allow_html=True)
        st.write("---")

# --- R2: Interpret (対応する和訳のみ) ---
with tabs[2]:
    st.subheader("Round 2: One-on-One Interpretation")
    st.write("その文に対応する意味だけを確認して、集中的にリピート。")
    for i, s in enumerate(sentences):
        with st.container(border=True):
            st.markdown(f'<p class="en-text">{format_slash(s)}</p>', unsafe_allow_html=True)
            # 対応するインデックスの和訳を表示
            if i < len(ja_sentences):
                st.markdown(f'<p class="ja-text">意味: {ja_sentences[i]}</p>', unsafe_allow_html=True)
            else:
                st.caption("(対応する和訳が見つかりません。改行で区切ってください)")
                
            if st.button(f"🔊 Listen", key=f"r2_{i}"):
                asyncio.run(generate_voice(s))
                st.markdown(get_audio_html("speech.mp3"), unsafe_allow_html=True)

# --- R3: Overlap ---
with tabs[3]:
    st.subheader("Round 3: Overlapping")
    speed_option = st.select_slider("再生スピード", options=["-20%", "-10%", "+0%", "+10%", "+20%"], value="+0%", key="r3_s")
    st.markdown(f'<p class="en-text">{format_slash(input_text)}</p>', unsafe_allow_html=True)
    if st.button("▶️ Start Overlapping"):
        asyncio.run(generate_voice(input_text, speed=speed_option))
        st.markdown(get_audio_html("speech.mp3"), unsafe_allow_html=True)

# --- R4: Shadow ---
with tabs[4]:
    st.subheader("Round 4: Shadowing")
    speed_shadow = st.select_slider("再生スピード", options=["-20%", "-10%", "+0%", "+10%", "+20%"], value="+0%", key="r4_s")
    if st.button("▶️ Start Shadowing"):
        asyncio.run(generate_voice(input_text, speed=speed_shadow))
        st.markdown(get_audio_html("speech.mp3"), unsafe_allow_html=True)

# --- R5: Performance ---
with tabs[5]:
    st.subheader("Round 5: Final Performance")
    st.markdown(f'<p class="en-text">{format_slash(input_text)}</p>', unsafe_allow_html=True)
    st.audio_input("最終パフォーマンスを録音")
    if st.button("🏁 Journey Complete!"):
        st.balloons()
