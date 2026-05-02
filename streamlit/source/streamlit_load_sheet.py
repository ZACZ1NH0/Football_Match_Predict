import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# =========================
# UI dịu mắt
# =========================
st.set_page_config(layout="wide")

st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #e6e6e6;
}
.card {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
}
.small-text {
    font-size: 14px;
    color: #aaa;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ EPL AI Predictor")

# =========================
# LOAD DATA
# =========================
url = "https://docs.google.com/spreadsheets/d/1qrbQTBuN3eSz1yDxpVQQ0r0aaGx_QhftJS5vMeIlnoA/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def load_data():
    df = conn.read(spreadsheet=url)

    cols = ["Elo_Diff", "Home_Win_Percent", "Away_Win_Percent", "Draw_Percent"]
    for col in cols:
        df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# =========================
# 🎯 CHỌN TRẬN
# =========================
st.subheader("🎯 Chọn trận để dự đoán")

teams = sorted(pd.concat([df['HomeTeam'], df['AwayTeam']]).unique())

c1, c2 = st.columns(2)
with c1:
    home = st.selectbox("Đội nhà", teams)
with c2:
    away = st.selectbox("Đội khách", teams)

if home != away:
    # Lấy trung bình xác suất từ data
    home_rate = df[df['HomeTeam'] == home]['Home_Win_Percent'].mean()
    away_rate = df[df['AwayTeam'] == away]['Away_Win_Percent'].mean()
    draw_rate = df['Draw_Percent'].mean()

    st.markdown("### 📊 Xác suất")

    col1, col2, col3 = st.columns(3)
    col1.metric("🏠 Home Win", f"{home_rate:.1f}%")
    col2.metric("🤝 Draw", f"{draw_rate:.1f}%")
    col3.metric("✈️ Away Win", f"{away_rate:.1f}%")

    # Kết luận
    if home_rate > away_rate and home_rate > draw_rate:
        st.success(f"👉 {home} thắng")
    elif away_rate > home_rate and away_rate > draw_rate:
        st.error(f"👉 {away} thắng")
    else:
        st.info("👉 Hòa")

else:
    st.warning("Chọn 2 đội khác nhau")

# =========================
# 🔥 10 TRẬN GẦN NHẤT (CARD VIEW)
# =========================
st.subheader("🔥 10 trận gần nhất")

df_recent = df.sort_values("Date", ascending=False).head(10)

for _, row in df_recent.iterrows():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([3, 1, 3])

    with c1:
        st.markdown(f"### 🏠 {row['HomeTeam']}")
    with c2:
        st.markdown("## vs")
    with c3:
        st.markdown(f"### ✈️ {row['AwayTeam']}")

    # Thanh xác suất (rất trực quan)
    st.progress(row["Home_Win_Percent"] / 100)

    st.caption(
        f"🏠 {row['Home_Win_Percent']:.1f}% | "
        f"🤝 {row['Draw_Percent']:.1f}% | "
        f"✈️ {row['Away_Win_Percent']:.1f}%"
    )

    # Result
    if row["Predict"] == "H":
        st.markdown("✅ **Chủ nhà thắng**")
    elif row["Predict"] == "A":
        st.markdown("🔴 **Đội khách thắng**")
    else:
        st.markdown("⚖️ **Hòa**")

    st.markdown(
        f"<div class='small-text'>📅 {row['Date'].date()}</div>",
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)