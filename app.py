import streamlit as st
import asyncio
import edge_tts
import base64
from notion_client import Client

# --- 1. Notion接続設定 ---
# 本番公開時は Streamlit Cloudの "Secrets" に保存します
if "NOTION_TOKEN" in st.secrets:
    notion = Client(auth=st.secrets["NOTION_TOKEN"])
    DATABASE_ID = st.secrets["NOTION_DATABASE_ID"]
else:
    st.error("Notionの設定が見つかりません。Secretsを設定してください。")
    st.stop()

# --- 2. 称号システム (ロードトリップ) ---
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

# URLから教材IDを取得 (?lesson=L1)
query_params = st.query_params
lesson_id = query_params.get("lesson", "L1")

# --- Notionから教材データを取得 ---
@st.cache_data(ttl=600)
def fetch_lesson(l_id):
    results = notion.databases.query(
        database_id=DATABASE_ID,
        filter={"property": "ID", "title": {"equals": l_id}}
    ).get("results")
    if results:
        props = results[0]["properties"]
        return {
            "title": props["Lesson Title"]["rich_text"][0]["plain_text"],
            "en": props["English Text"]["rich_text"][0]["plain_text"],
            "ja": props["Japanese Translation"]["rich_text"][0]["plain_text"]
        }
    return None

lesson_data = fetch_lesson(lesson_id)

if not lesson_data:
    st.warning(f"教材 '{lesson_id}' が見つかりません。Notionを確認してください。")
    st.stop()

# サイドバー
with st.sidebar:
    st.title("🗺️ My Progress")
    user_name = st.text_input("Name", "Student")
    total_comp = st.number_input("Total Completes", 0) # 本来はログDBから集計
    rank, city, icon, color = get_rank(total_comp)
    st.markdown(f"<div style='background-color:{color}; padding:15px; border-radius:10px; color:white; text-align:center;'><h3>{icon} {rank}</h3><p>{city}</p></div>", unsafe_allow_html=True)

# 修行画面
st.title(f"🚀 {lesson_data['title']}")
tabs = st.tabs(["R0: Intro", "R1-R4: Training", "R5: Final"])

with tabs[0]:
    st.subheader("Meaning Check")
    st.info(lesson_data['en'])
    st.success(lesson_data['ja'])

with tabs[1]:
    mode = st.radio("Mode", ["R1: Repeating", "R4: Shadowing"])
    if mode == "R1: Repeating":
        st.write(lesson_data['en'])
    else:
        st.write("*(Text Hidden)*")
    
    if st.button("🔊 Listen"):
        asyncio.run(generate_voice(lesson_data['en']))
        with open("speech.mp3", "rb") as f:
            st.audio(f.read(), format="audio/mp3")

with tabs[2]:
    st.subheader("Final Performance")
    st.write("録音して修行を完了しましょう！")
    if st.button("🏁 修行完了ボタンを押す"):
        # ここでNotionのログDBに書き込む処理を追加可能
        st.balloons()
        st.success(f"Good job, {user_name}! You've reached {city}!")
