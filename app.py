import streamlit as st
import asyncio
import edge_tts
import base64
import os

# --- 1. 称号システム (Road Trip) ---
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

# --- 2. 音声生成ロジック ---
async def generate_voice(text):
    # 以前の音声ファイルを削除して重複を避ける
    if os.path.exists("speech.mp3"):
        os.remove("speech.mp3")
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save("speech.mp3")

# --- 3. メインUI設定 ---
st.set_page_config(page_title="English Road Trip", layout="wide")

# サイドバー (進捗表示)
with st.sidebar:
    st.title("🗺️ My Progress")
    user_name = st.text_input("Name", "Student")
    total_comp = st.number_input("Total Completes", 0, step=1)
    rank, city, icon, color = get_rank(total_comp)
    st.markdown(f"""
    <div style='background-color:{color}; padding:20px; border-radius:10px; color:white; text-align:center;'>
        <h2>{icon} {rank}</h2>
        <p>Current: {city}</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.caption("授業で使う場合は、先生から送られたテキストを貼り付けてください。")

# --- 4. テキスト入力エリア ---
st.title("🚀 English Road Trip: Free Practice")

# ここで自由にテキストを入れられるようにします
st.subheader("1. 練習したいテキストを入力してください")
input_text = st.text_area("English Text", placeholder="Paste your English text here...", height=150)
input_ja = st.text_area("Japanese Meaning (Optional)", placeholder="日本語訳（任意）", height=100)

if not input_text:
    st.info("👆 上のボックスに英文を貼り付けると、修行がスタートします！")
    st.stop()

# --- 5. 修行コンテンツ ---
st.divider()
tab0, tab1, tab2 = st.tabs(["📖 Reading", "🎧 Training", "🏁 Finish"])

with tab0:
    st.subheader("Text & Meaning")
    st.info(input_text)
    if input_ja:
        with st.expander("日本語訳を表示"):
            st.write(input_ja)

with tab1:
    st.subheader("Audio Training")
    mode = st.radio("Practice Mode", ["Visible (R1-R3)", "Hidden (R4)"])
    
    if mode == "Visible (R1-R3)":
        st.info(input_text)
    else:
        st.warning("耳に集中しましょう！(Text Hidden)")
    
    if st.button("🔊 Play Voice"):
        with st.spinner("Preparing Audio..."):
            asyncio.run(generate_voice(input_text))
            with open("speech.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

with tab2:
    st.subheader("Goal!")
    if st.button("Complete Journey"):
        st.balloons()
        st.success(f"Well done, {user_name}! You've made progress toward {city}!")
