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
    # speedの形式は "+10%" や "-10%"
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate=speed)
    await communicate.save("speech.mp3")

def play_audio():
    if os.path.exists("speech.mp3"):
        with open("speech.mp3", "rb") as f:
            st.audio(f.read(), format="audio/mp3")

# --- 3. UI設定 ---
st.set_page_config(page_title="English Road Trip", layout="wide")

with st.sidebar:
    st.title("🗺️ My Progress")
    user_name = st.text_input("Name", "Student")
    total_comp = st.number_input("Total Completes", 0, step=1)
    rank, city, icon, color = get_rank(total_comp)
    st.markdown(f"<div style='background-color:{color}; padding:20px; border-radius:10px; color:white; text-align:center;'><h2>{icon} {rank}</h2><p>{city}</p></div>", unsafe_allow_html=True)

st.title("🚀 English Road Trip: Intensive Training")

# --- 4. テキスト入力エリア ---
with st.expander("📝 教材をセットする", expanded=True):
    input_text = st.text_area("English Text", placeholder="英文を入力...", height=150)
    input_ja = st.text_area("Japanese Translation", placeholder="和訳を入力...", height=100)

if not input_text:
    st.info("英文を貼り付けて修行を開始しましょう！")
    st.stop()

# テキストを一文ごとに分割する（ピリオド、クエスチョンマークなどで区切る）
sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', input_text) if s.strip()]

# --- 5. 修行ステップ ---
st.divider()
tabs = st.tabs(["R0: Intro", "R1: Repeat", "R2: Interpret", "R3: Overlap", "R4: Shadow", "R5: Performance"])

# --- R0: 一回声に出して読む ---
with tabs[0]:
    st.subheader("Round 0: Orientation")
    st.write("まずは全体を確認して、一度声に出して読んでみましょう。")
    col1, col2 = st.columns(2)
    with col1:
        st.info(input_text)
    with col2:
        st.success(input_ja)
    st.audio_input("音読を記録 (R0)")

# --- R1: 一文ごとのリピーティング ---
with tabs[1]:
    st.subheader("Round 1: Sentence Repeating")
    st.write("一文ずつ聞いて、後に続いてリピートしてください。")
    for i, s in enumerate(sentences):
        col_s, col_p = st.columns([4, 1])
        col_s.write(f"{i+1}. {s}")
        if col_p.button(f"Play {i+1}", key=f"r1_{i}"):
            asyncio.run(generate_voice(s))
            play_audio()

# --- R2: 意味を確認してリピーティング ---
with tabs[2]:
    st.subheader("Round 2: Interpretation & Repeat")
    st.write("和訳を確認しながら、一文ずつリピート。")
    # ここでは和訳も一文ずつ出すために、入力された和訳も分割を試みる
    ja_sentences = [j.strip() for j in re.split(r'(?<=[。！？]) +', input_ja) if j.strip()]
    
    for i, s in enumerate(sentences):
        with st.container(border=True):
            st.write(f"EN: {s}")
            if i < len(ja_sentences):
                st.caption(f"JA: {ja_sentences[i]}")
            if st.button(f"Listen {i+1}", key=f"r2_{i}"):
                asyncio.run(generate_voice(s))
                play_audio()

# --- R3: オーバーラッピング（スピード調整付） ---
with tabs[3]:
    st.subheader("Round 3: Overlapping")
    st.write("音声と同時に発音します。最後まで一気に流れます。")
    speed_option = st.select_slider("再生スピード", options=["-20%", "-10%", "+0%", "+10%", "+20%"], value="+0%")
    st.info(input_text)
    if st.button("Start Overlapping"):
        asyncio.run(generate_voice(input_text, speed=speed_option))
        play_audio()

# --- R4: シャドーイング（文字なし） ---
with tabs[4]:
    st.subheader("Round 4: Shadowing")
    st.warning("文字は見えません。耳だけで追いかけてください！")
    speed_shadow = st.select_slider("再生スピード (Shadowing)", options=["-20%", "-10%", "+0%", "+10%", "+20%"], value="+0%", key="shadow_speed")
    if st.button("Start Shadowing"):
        asyncio.run(generate_voice(input_text, speed=speed_shadow))
        play_audio()

# --- R5: 本番音読 ---
with tabs[5]:
    st.subheader("Round 5: Final Performance")
    st.write("日本語をイメージしながら、気持ちを込めて音読しましょう。")
    st.info(input_text)
    st.audio_input("最終パフォーマンスを録音")
    if st.button("Complete Journey!"):
        st.balloons()
        st.success(f"Congratulation, {user_name}! You've reached {city}!")
