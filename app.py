import streamlit as st
import asyncio
import edge_tts
import base64
import os

# --- 1. アプリの設定と世界観 ---
st.set_page_config(page_title="English Road Trip", layout="wide")

# ロードトリップの称号設定
def get_rank(completes):
    if completes >= 50: return "West Coast Legend", "San Francisco", "🔥", "#000000"
    if completes >= 25: return "Grand Canyon Explorer", "Arizona", "🔮", "#008080"
    if completes >= 10: return "Route 66 Rider", "Mid-West", "🥇", "#FFD700"
    if completes >= 5:  return "Jazz Traveler", "New Orleans", "🥈", "#C0C0C0"
    if completes >= 1:  return "NYC Tourist", "New York", "🥉", "#CD7F32"
    return "Starting Line", "New York", "🚗", "#808080"

# --- 2. 音声生成エンジン (Edge TTS) ---
async def generate_voice(text, output_file="speech.mp3"):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(output_file)

def play_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
        st.markdown(md, unsafe_allow_html=True)

# --- 3. サイドバー (進捗管理) ---
with st.sidebar:
    st.title("🗺️ My Progress")
    user_name = st.text_input("Name", value="Toshi")
    # 本来はNotionから取得するコンプリート数
    total_comp = st.number_input("Total Completes", min_value=0, step=1, value=0)
    
    rank, city, icon, color = get_rank(total_comp)
    
    st.markdown(f"""
    <div style="background-color:{color}; padding:20px; border-radius:10px; color:white; text-align:center;">
        <h2 style="margin:0;">{icon} {rank}</h2>
        <p style="margin:0;">Current: {city}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    if st.button("発音クリニックを開く"):
        st.info("L/R, TH, 母音の練習メニュー（準備中）")

# --- 4. メインコンテンツ (教材) ---
st.title("🚀 English Road Trip: Practice")

# 教材データ（本来はNotionから取得）
target_text = "I have a dream that one day this nation will rise up and live out the true meaning of its creed."
target_ja = "私には夢がある。いつの日か、この国が立ち上がり、その信条の真の意味を実践することを。"

# Roundの選択
rounds = ["R0: Intro", "R1: Repeat", "R2: Interpret", "R3: Copying", "R4: Shadow", "R5: Perf"]
selected_round = st.select_slider("修行ラウンドを選択", options=rounds)

st.divider()

if selected_round == "R0: Intro":
    st.subheader("Round 0: 意味を確認しよう")
    col1, col2 = st.columns(2)
    with col1:
        st.info(target_text)
    with col2:
        st.success(target_ja)

elif selected_round == "R1: Repeat":
    st.subheader("Round 1: リピーティング")
    st.write("英文を聞いた後、ポーズの間にリピートしてください。")
    st.info(target_text)
    if st.button("再生"):
        asyncio.run(generate_voice(target_text))
        play_audio("speech.mp3")

elif selected_round == "R4: Shadow":
    st.subheader("Round 4: シャドーイング")
    st.warning("英文は隠しました。耳だけで追いかけてください！")
    # テキストを表示しない
    if st.button("音声スタート"):
        asyncio.run(generate_voice(target_text))
        play_audio("speech.mp3")

elif selected_round == "R5: Perf":
    st.subheader("Round 5: 魂の音読")
    st.write("意味をイメージしながら、自分の声で録音しましょう。")
    st.info(target_text)
    st.button("🔴 録音スタート (Mock)")
    if st.button("修行完了！"):
        st.balloons()
        st.confetti()
        st.success("コンプリート！ロードトリップの歩みが進みました。")
