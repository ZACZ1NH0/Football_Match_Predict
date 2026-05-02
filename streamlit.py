import streamlit as st
import pandas as pd
import numpy as np
import duckdb
import requests
from st_gsheets_connection import GSheetsConnection
# from streamlit_gsheets import GSheetsConnection
from langchain.agents import tool, AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN
# ==========================================
st.set_page_config(
    page_title="EPL Elite Prediction Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: var(--background-color); }
    .prediction-card {
        background-color: var(--secondary-background-color);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-top: 5px solid #ff2882;
        margin-bottom: 20px;
        color: var(--text-color);
    }
    .metric-title {
        color: var(--text-color);
        opacity: 0.8;
        font-size: 1rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    .score-box {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin: 15px 0;
    }
    .score-value {
        font-size: 3.2rem;
        font-weight: 800;
        color: var(--text-color);
    }
    .vs-text {
        font-size: 1.4rem;
        color: #ff2882;
        font-weight: bold;
    }
    .pred-text {
        text-align: center;
        font-weight: bold;
        margin-top: 10px;
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HÀM LOAD DỮ LIỆU & SETUP
# ==========================================
@st.cache_data(ttl=600)
def load_all_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    urls = {
        "results": os.getenv("RESULTS_URL"),
        "goals": os.getenv("GOAL_URL"),
        "corners": os.getenv("CORNER_URL"),
        "cards": os.getenv("CARD_URL"),
        "ranking": os.getenv("RANKING_URL")
    }
    df_res = conn.read(spreadsheet=urls["results"])
    df_gls = conn.read(spreadsheet=urls["goals"])
    df_cnr = conn.read(spreadsheet=urls["corners"])
    df_crd = conn.read(spreadsheet=urls["cards"])
    df_ran = conn.read(spreadsheet=urls["ranking"])
    for df in [df_res, df_gls, df_cnr, df_crd]:
        df['Date'] = pd.to_datetime(df['Date'])
        
    return df_res, df_gls, df_cnr, df_crd, df_ran

df_res, df_gls, df_cnr, df_crd, df_ran = load_all_data()

for df in [df_res, df_gls, df_cnr, df_crd, df_ran]:
    for col in df.columns:
        if 'Percent' in col or col in ['Home', 'Away', 'xG_Home', 'xG_Away']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

# Setup DuckDB In-Memory
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = duckdb.connect(database=':memory:', read_only=False)
    st.session_state.db_conn.register('results', df_res)
    st.session_state.db_conn.register('goals', df_gls)
    st.session_state.db_conn.register('corners', df_cnr)
    st.session_state.db_conn.register('cards', df_crd)

# ==========================================
# 3. ĐỊNH NGHĨA MCP TOOLS CHO AI
# ==========================================
@tool
def execute_sql_query(query: str) -> str:
    """Chạy câu lệnh SQL trên DuckDB. Bảng: results, goals, corners, cards."""
    try:
        return st.session_state.db_conn.execute(query).df().to_string()
    except Exception as e:
        return f"Lỗi SQL: {str(e)}"

@tool
def get_match_context(home_team: str, away_team: str) -> str:
    """Lấy bối cảnh định tính của trận đấu (tính chất Derby)."""
    derbies = {
        ("Arsenal", "Tottenham"): "North London Derby - Cực kỳ căng thẳng, rủi ro thẻ phạt cao.",
        ("Man Utd", "Man City"): "Manchester Derby - Áp lực tâm lý khổng lồ, danh dự thành phố.",
        ("Liverpool", "Everton"): "Merseyside Derby - Lối chơi quyết liệt, va chạm nhiều.",
        ("Chelsea", "Arsenal"): "London Derby - Đậm tính chiến thuật và kiểm soát."
    }
    match_pair = (home_team, away_team)
    if match_pair in derbies: return f"Tính chất trận đấu: {derbies[match_pair]}"
    elif (away_team, home_team) in derbies: return f"Tính chất trận đấu: {derbies[(away_team, home_team)]}"
    return "Đây là trận đấu giải vòng tròn thông thường."

@tool
def get_injury_news(team_name: str) -> str:
    """
    Lấy danh sách chấn thương, treo giò của đội bóng từ FPL API.
    Đã được lọc chuẩn xác, loại bỏ các cầu thủ đã chuyển nhượng hoặc đem cho mượn.
    """
    name_mapping = {
        "Tottenham": "Spurs", "Nottingham": "Nott'm Forest", 
        "Nottingham Forest": "Nott'm Forest", "Man United": "Man Utd", 
        "Manchester United": "Man Utd", "Man City": "Man City", 
        "Manchester City": "Man City", "Newcastle Utd": "Newcastle"
    }
    fpl_team_name = name_mapping.get(team_name, team_name)
    
    try:
        data = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        
        # Tìm ID đội bóng
        team_id = next((t['id'] for t in data['teams'] if t['name'].lower() == fpl_team_name.lower() or t['short_name'].lower() == fpl_team_name.lower()), None)
        if not team_id: return f"Không tìm thấy mã ID của đội {team_name}."
        
        injuries = []
        for p in data['elements']:
            if p['team'] == team_id:
                status = p.get('status', '')
                news = p.get('news', '').lower()
                
                # FPL Status codes: 'i' (Injured), 's' (Suspended), 'd' (Doubtful)
                # Các trạng thái như 'u' (Unavailable) hoặc 'n' thường là chuyển nhượng/rời đội
                # Thêm lớp lọc từ khóa: Nếu trong news có chữ 'loan', 'joined', 'transferred', 'left' thì bỏ qua
                transfer_keywords = ['loan', 'joined', 'transferred', 'left', 'permanent']
                is_transferred = any(kw in news for kw in transfer_keywords)
                
                if status in ['i', 's', 'd'] and not is_transferred:
                    name = p['web_name']
                    reason = p['news']
                    chance = p.get('chance_of_playing_this_round', 0)
                    injuries.append(f"- {name}: {reason} (Khả năng ra sân: {chance}%)")
        
        if not injuries:
            return f"Nhân sự {team_name}: Không ghi nhận chấn thương/treo giò nghiêm trọng nào trong đội hình hiện tại."
            
        return f"Nhân sự {team_name} (Chỉ tính chấn thương/treo giò):\n" + "\n".join(injuries)
        
    except Exception as e:
        return f"Lỗi cào dữ liệu FPL: {str(e)}"

@tool
def get_team_key_players(team_name: str) -> str:
    """
    Lấy danh sách các cầu thủ chủ chốt ĐANG THI ĐẤU cho đội bóng ở thời điểm hiện tại và có phong độ cao nhất.
    Giúp AI cập nhật đúng nhân sự thực tế, tránh nhắc đến các cầu thủ đã chuyển nhượng trong quá khứ.
    """
    name_mapping = {"Tottenham": "Spurs", "Nottingham": "Nott'm Forest", "Nottingham Forest": "Nott'm Forest", "Man United": "Man Utd", "Manchester United": "Man Utd", "Man City": "Man City", "Manchester City": "Man City", "Newcastle Utd": "Newcastle"}
    fpl_team_name = name_mapping.get(team_name, team_name)
    
    try:
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(url)
        data = response.json()
        
        # Tìm ID đội bóng
        team_id = next((t['id'] for t in data['teams'] if t['name'].lower() == fpl_team_name.lower() or t['short_name'].lower() == fpl_team_name.lower()), None)
        if not team_id: return f"Không tìm thấy dữ liệu đội hình của {team_name}."
        
        # Lọc cầu thủ của đội hiện tại
        team_players = [p for p in data['elements'] if p['team'] == team_id]
        
        # Sắp xếp theo phong độ (form) giảm dần, lấy top 5 người gánh team
        # Note: 'form' trong API FPL trả về dạng chuỗi (ví dụ: "5.5") nên cần ép kiểu float
        top_players = sorted(team_players, key=lambda x: float(x['form']), reverse=True)[:5]
        
        positions = {1: 'Thủ môn', 2: 'Hậu vệ', 3: 'Tiền vệ', 4: 'Tiền đạo'}
        
        res = [f"- {p['web_name']} ({positions.get(p['element_type'], 'Cầu thủ')} | Điểm phong độ: {p['form']})" for p in top_players]
        
        return f"Top 5 cầu thủ chủ chốt HIỆN TẠI của {team_name} (Dựa trên phong độ):\n" + "\n".join(res)
        
    except Exception as e:
        return f"Lỗi cào dữ liệu phong độ FPL: {str(e)}"
    
@tool
def get_standings_and_context(home_team: str, away_team: str) -> str:
    """
    Công cụ quan trọng: Lấy thông tin Vòng đấu (Matchweek) và Thứ hạng (Rank) 
    hiện tại của đội nhà (Home_Rank) và đội khách (Away_Rank) từ database.
    """
    try:
        # Lấy connection DuckDB từ session_state của Streamlit
        if 'db_conn' not in st.session_state:
            return "Lỗi: Không tìm thấy kết nối Database DuckDB."
            
        conn = st.session_state.db_conn
        
        # Câu lệnh SQL truy vấn trực tiếp vào bảng 'results'
        # Dùng dấu ? để truyền biến, chống lỗi cú pháp khi tên đội có dấu nháy đơn
        query = """
            SELECT Matchweek, Home_Rank, Away_Rank 
            FROM results 
            WHERE HomeTeam = ? AND AwayTeam = ?
            LIMIT 1
        """
        
        # Thực thi và lấy dòng đầu tiên
        result = conn.execute(query, (home_team, away_team)).fetchone()
        
        if result:
            matchweek = result[0]
            home_rank = result[1]
            away_rank = result[2]
            
            # Format chuỗi trả về cho LLM đọc
            context_str = (
                f"Trận đấu thuộc Vòng (Matchweek): {matchweek}\n"
                f"- Thứ hạng {home_team} (Đội nhà): Hạng {home_rank}\n"
                f"- Thứ hạng {away_team} (Đội khách): Hạng {away_rank}\n"
                f"Ghi chú: Đội có thứ hạng số càng nhỏ (gần 1) là đội mạnh hơn, đứng cao hơn trên bảng xếp hạng."
            )
            return context_str
        else:
            return f"Không tìm thấy dữ liệu vòng đấu và thứ hạng cho trận {home_team} vs {away_team} trong bảng results."
            
    except Exception as e:
        return f"Lỗi khi query DuckDB: {str(e)}"
    

tools = [execute_sql_query, get_match_context, get_injury_news, get_team_key_players, get_standings_and_context]

# ==========================================
# 5. TRANG CHỦ & TỔNG QUAN
# ==========================================
st.title("EPL Prediction Elite Dashboard")
st.divider()
st.header("Dự Báo Cục Diện Mùa Giải (Siêu Máy Tính)")
st.info("Kết quả dựa trên 10,000 lần mô phỏng các trận đấu còn lại của mùa giải.")

# Tạo Tabs để phân loại nội dung
tabb1, tabb2, tabb3 = st.tabs([" Bảng Tổng Hợp", " Cuộc Đua Top 4", " Nguy Cơ Xuống Hạng"])

cols_to_fix = ["Điểm TB Dự Kiến", "Xác suất Vô Địch (%)", "Xác suất Top 4 (%)", "Xác suất Xuống Hạng (%)"]

for col in cols_to_fix:
    if col in df_ran.columns:
        # Chuyển đổi thành string -> thay dấu phẩy bằng dấu chấm -> chuyển thành float
        df_ran[col] = pd.to_numeric(df_ran[col].astype(str).str.replace(',', '.'), errors='coerce')
with tabb1:
    st.subheader("Bảng Điểm Dự Kiến & Xác Suất")
    
    # Cấu hình hiển thị bảng đẹp với Progress Bar
    st.dataframe(
        df_ran,
        column_config={
            "Đội Bóng": st.column_config.TextColumn("Đội bóng", width="medium"),
            "Điểm TB Dự Kiến": st.column_config.NumberColumn("Điểm TB", format="%.1f"),
            "Xác suất Vô Địch (%)": st.column_config.ProgressColumn(
                "Vô Địch", help="Tỉ lệ về đích vị trí số 1", format="%.1f%%", min_value=0, max_value=100
            ),
            "Xác suất Top 4 (%)": st.column_config.ProgressColumn(
                "Top 4 (CL)", help="Tỉ lệ dự Champions League", format="%.1f%%", min_value=0, max_value=100
            ),
            "Xác suất Xuống Hạng (%)": st.column_config.ProgressColumn(
                "Xuống Hạng", help="Tỉ lệ rơi vào nhóm 3 đội cuối bảng", format="%.1f%%", min_value=0, max_value=100
            ),
        },
        hide_index=True,
        use_container_width=True
    )

with tabb2:
    st.subheader("Top 6 Đội Có Khả Năng Dự Champions League Cao Nhất")
    # Lấy Top 6 theo xác suất Top 4
    top_cl = df_ran.sort_values("Xác suất Top 4 (%)", ascending=False).head(6)
    
    # Hiển thị biểu đồ cột ngang cho trực quan
    st.bar_chart(
        top_cl, 
        x="Đội Bóng", 
        y="Xác suất Top 4 (%)", 
        color="#2ecc71" # Màu xanh hy vọng
    )
    
    # Hiển thị nhanh dưới dạng Metric cho Top 3
    m1, m2, m3 = st.columns(3)
    with m1: st.metric(top_cl.iloc[0]["Đội Bóng"], f"{top_cl.iloc[0]['Xác suất Top 4 (%)']:.1f}% CL")
    with m2: st.metric(top_cl.iloc[1]["Đội Bóng"], f"{top_cl.iloc[1]['Xác suất Top 4 (%)']:.1f}% CL")
    with m3: st.metric(top_cl.iloc[2]["Đội Bóng"], f"{top_cl.iloc[2]['Xác suất Top 4 (%)']:.1f}% CL")

with tabb3:
    st.subheader("Nhóm Đội Đang Trong Vùng Nguy Hiểm")
    # Lọc các đội có xác suất xuống hạng > 1%
    relegation_zone = df_ran[df_ran["Xác suất Xuống Hạng (%)"] > 1].sort_values("Xác suất Xuống Hạng (%)", ascending=False)
    
    if not relegation_zone.empty:
        st.bar_chart(
            relegation_zone, 
            x="Đội Bóng", 
            y="Xác suất Xuống Hạng (%)", 
            color="#ff4b4b" # Màu đỏ cảnh báo
        )
        st.warning(f"Có {len(relegation_zone)} đội bóng đang có nguy cơ xuống hạng dựa trên mô phỏng.")
    else:
        st.success("Dữ liệu mô phỏng hiện chưa ghi nhận nguy cơ xuống hạng cao cho các đội.")

st.caption("Lưu ý: Các con số trên mang tính chất tham khảo từ mô hình toán học và không đảm bảo kết quả thực tế.")

# Chi tiết bảng xếp hạng hiện tại và các trận sắp tới

top_col1, top_col2 = st.columns([1, 1.2])
st.image("https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg", width=100)

with top_col1:
    st.subheader("Bảng Xếp Hạng Hiện Tại")
    latest_home = df_res.sort_values('Date', ascending=False).drop_duplicates('HomeTeam')[['HomeTeam', 'Home_Rank']]
    latest_away = df_res.sort_values('Date', ascending=False).drop_duplicates('AwayTeam')[['AwayTeam', 'Away_Rank']]
    ranks = pd.concat([latest_home.rename(columns={'HomeTeam': 'Team', 'Home_Rank': 'Rank'}), latest_away.rename(columns={'AwayTeam': 'Team', 'Away_Rank': 'Rank'})])
    standings = ranks.groupby('Team')['Rank'].min().sort_values().reset_index()
    st.dataframe(standings.rename(columns={'Team': 'Đội Bóng', 'Rank': 'Hạng'}), use_container_width=True, hide_index=True)

with top_col2:
    st.subheader("10 Trận Sắp Diễn Ra")
    upcoming = df_res.sort_values('Date', ascending=True).tail(10).copy()
    def get_insight(row):
        h_prob, a_prob = float(str(row['Home_Win_Percent']).replace(',', '.')), float(str(row['Away_Win_Percent']).replace(',', '.'))
        diff = abs(h_prob - a_prob)
        if diff < 3.0: return "Cực kỳ cân bằng (Dễ Hòa)"
        elif diff < 8.0: return "Khá cân bằng"
        elif h_prob > a_prob: return f"{row['HomeTeam']} nhỉnh hơn"
        else: return f"{row['AwayTeam']} nhỉnh hơn"
    upcoming['Nhận Định'] = upcoming.apply(get_insight, axis=1)
    st.dataframe(upcoming[['Date', 'HomeTeam', 'AwayTeam', 'Nhận Định']], use_container_width=True, hide_index=True)

# FILTER
st.header("Lọc Trận Đấu")
all_teams = sorted(df_res['HomeTeam'].unique())
col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("Chọn Đội Chủ Nhà", all_teams, index=all_teams.index("Arsenal") if "Arsenal" in all_teams else 0)
with col2:
    away_team = st.selectbox("Chọn Đội Khách", all_teams, index=all_teams.index("Man City") if "Man City" in all_teams else 1)

st.divider()

# ==========================================
# 6. CHI TIẾT DỰ ĐOÁN (ĐỊNH LƯỢNG)
# ==========================================
st.header(f"Phân Tích Đối Đầu: {home_team} vs {away_team}")
match_res = df_res[(df_res['HomeTeam'] == home_team) & (df_res['AwayTeam'] == away_team)].iloc[:1]
match_gls = df_gls[(df_gls['HomeTeam'] == home_team) & (df_gls['AwayTeam'] == away_team)].iloc[:1]
match_cnr = df_cnr[(df_cnr['HomeTeam'] == home_team) & (df_cnr['AwayTeam'] == away_team)].iloc[:1]
match_crd = df_crd[(df_crd['HomeTeam'] == home_team) & (df_crd['AwayTeam'] == away_team)].iloc[:1]

if not match_res.empty:
    st.subheader("Xác Suất Kết Quả")
    p1, p2, p3 = st.columns(3)
    p1.metric(f"{home_team} Thắng", f"{match_res['Home_Win_Percent'].values[0]:.1f}%")
    p2.metric("Hòa", f"{match_res['Draw_Percent'].values[0]:.1f}%")
    p3.metric(f"{away_team} Thắng", f"{match_res['Away_Win_Percent'].values[0]:.1f}%")
    st.progress(match_res['Home_Win_Percent'].values[0] / 100, text="Tỉ lệ thắng Đội Nhà")

    st.subheader("Dự Đoán Thông Số Chi Tiết")
    col_a, col_b, col_c = st.columns(3)
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><span style='color: var(--text-color); font-weight: bold; border-bottom: 3px solid var(--text-color); padding-bottom: 3px;'>{home_team}</span><span style='margin: 0 20px; color: #888;'>|</span><span style='color: #ff2882; font-weight: bold; border-bottom: 3px solid #ff2882; padding-bottom: 3px;'>{away_team}</span></div>", unsafe_allow_html=True)
    
    with col_a:
        st.markdown(f"<div class='prediction-card'><div class='metric-title'>BÀN THẮNG DỰ KIẾN (xG)</div><div class='score-box'><span class='score-value'>{match_gls['xG_Home'].values[0]:.2f}</span><span class='vs-text'>VS</span><span class='score-value' style='color:#ff2882;'> {match_gls['xG_Away'].values[0]:.2f}</span></div></div>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<div class='prediction-card'><div class='metric-title'>PHẠT GÓC DỰ KIẾN</div><div class='score-box'><span class='score-value'>{match_cnr['Home'].values[0]:.1f}</span><span class='vs-text'>VS</span><span class='score-value' style='color:#ff2882;'>{match_cnr['Away'].values[0]:.1f}</span></div></div>", unsafe_allow_html=True)
    with col_c:
        st.markdown(f"<div class='prediction-card'><div class='metric-title'>THẺ PHẠT DỰ KIẾN</div><div class='score-box'><span class='score-value'>{match_crd['Home'].values[0]:.2f}</span><span class='vs-text'>VS</span><span class='score-value' style='color:#ff2882;'>{match_crd['Away'].values[0]:.2f}</span></div></div>", unsafe_allow_html=True)
    
    st.subheader("Lịch Sử Đối Đầu (Head-to-Head)")
    h2h_1, h2h_2, h2h_3, h2h_4 = st.columns(4)
    h2h_1.metric(f"{home_team} thắng", match_res['Home_H2H_Wins'].values[0])
    h2h_2.metric("Hòa", match_res['H2H_Draws'].values[0])
    h2h_3.metric(f"{away_team} thắng", match_res['Away_H2H_Wins'].values[0])
    h2h_4.metric("Vòng đấu", f"Match Week {int(match_res['Matchweek'].values[0])}")
else:
    st.warning("Không tìm thấy dữ liệu cho cặp đấu này.")

# ==========================================
# 7. AI DEEP MATCH ANALYSIS
# ==========================================
st.divider()

# Cấu hình LLM dùng chung cho cả Feature 1 & 2
system_prompt_global = """
Bạn là Chuyên gia Phân tích Dữ liệu Thể thao chuyên nghiệp. LUÔN dùng tool để lấy dữ liệu, không tự bịa.
TUYỆT ĐỐI KHÔNG bàn luận, phân tích, hay đề cập đến tỷ lệ cá cược, kèo cược, cờ bạc dưới mọi hình thức.
Chỉ phân tích chuyên môn: chiến thuật, phong độ, xG, phạt góc, thẻ phạt, chấn thương.
"""

def get_agent_executor(llm_model, api_key):
    llm = ChatGroq(
        temperature=0.3,
        groq_api_key= os.getenv("GROQ_API_KEY"), 
        model_name = "llama-3.3-70b-versatile",
        max_retries=2
    )
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt_global),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt_template)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
tab1, tab2 = st.tabs(["Phân tích chuyên sâu trận đấu", "Truy vấn trên các trận đã diễn ra"])
with tab1:
    st.header("Phân tích chi tiết")
    st.markdown("Hệ thống Agent tự động thu thập dữ liệu định lượng (ML) và bối cảnh định tính (Chấn thương, Derby) để đưa ra nhận định chuyên sâu.")
    if st.button(f"Phân Tích Chuyên Sâu: {home_team} vs {away_team}", type="primary", use_container_width=True):
        if not openrouter_key:
            st.error("Chưa có API KEY")
        else:
            with st.spinner("AI đang phân tích dữ liệu DuckDB và cào thông tin chấn thương từ FPL..."):
                agent_executor = get_agent_executor(model_choice, openrouter_key)
                agent_task = f"""
                    Bạn là một Chuyên gia Phân tích Dữ liệu Bóng đá cấp cao. Nhiệm vụ của bạn là thực hiện bản "Deep Match Analysis" (Phân tích Chuyên sâu) cho trận đấu: {home_team} (Sân nhà) vs {away_team} (Sân khách).

                    PHẦN 1: QUY TRÌNH THU THẬP DỮ LIỆU BẮT BUỘC (TOOL CALLING)
                    Bạn PHẢI gọi lần lượt và đầy đủ các công cụ sau trước khi viết bất kỳ lời bình luận nào:
                    1. Gọi 'execute_sql_query': Lấy toàn bộ số liệu định lượng từ mô hình học máy (xG dự kiến, xác suất Thắng/Hòa/Thua, dự đoán số thẻ/góc).
                    2. Gọi 'get_match_context': Lấy thông tin về bối cảnh lịch sử, mức độ thù địch hoặc tính chất căng thẳng của cặp đấu này.
                    3. Gọi 'get_injury_news': Gọi 2 lần (một cho {home_team}, một cho {away_team}) để xác định danh sách các trụ cột vắng mặt.
                    4. Gọi 'get_team_key_players': Gọi 2 lần (một cho {home_team}, một cho {away_team}) để lấy danh sách cầu thủ đang có phong độ cao nhất hiện tại.
                    5. Gọi 'get_standings_and_context': Lấy thông tin về Home_Rank, Away_Rank và Matchweek để đưa ra nhận định mức độ quan trọng của cặp đấu này
                    PHẦN 2: CẤU TRÚC BÁO CÁO PHÂN TÍCH (XUẤT RA BẰNG MARKDOWN)
                    Sau khi thu thập đủ dữ liệu, BẮT BUỘC viết báo cáo chi tiết, phân tích sâu sắc. MỖI MỤC DƯỚI ĐÂY PHẢI ĐƯỢC PHÂN TÍCH ÍT NHẤT 150-200 CHỮ:

                    ### 📊 1. Giải mã Số liệu Định lượng (Quantitative Decoding)
                    - Không chỉ liệt kê con số, hãy DIỄN GIẢI ý nghĩa của chúng. Ví dụ: xG của đội nhà cao hơn nghĩa là họ áp đảo lối chơi thế nào? Xác suất thẻ/góc phản ánh nhịp độ trận đấu ra sao?

                    ### ⚔️ 2. Điểm nóng Chiến thuật & Biến số Nhân sự
                    - Đào sâu vào sự đối đầu của các "Cầu thủ chủ chốt hiện tại". Nếu họ đối đầu nhau trên sân, kịch bản nào sẽ xảy ra?
                    - Phân tích chi tiết lỗ hổng chiến thuật nếu có "Trụ cột chấn thương/vắng mặt". Đội hình sẽ bị xáo trộn ra sao và ảnh hưởng thế nào đến con số xG dự kiến?

                    ### ⚠️ 3. Bối cảnh Lịch sử & Rủi ro Phá vỡ Mô hình (Contextual Risks)
                    - Đánh giá mức độ thù địch của cặp đấu này. Tính chất căng thẳng của trận đấu sẽ đẩy số lượng thẻ phạt và phạt góc lên cao như thế nào so với dự đoán của mô hình thuật toán?

                    ### 🎯 4. Kết luận Chuyên sâu (Final Verdict)
                    - Tổng hợp lại: Yếu tố nào (Dữ liệu thuật toán hay Bối cảnh con người) sẽ đóng vai trò quyết định cục diện trận đấu này? Đưa ra kịch bản diễn biến chi tiết. Kết quả trận đấu chung cuộc.

                    PHẦN 3: 🛑 NHỮNG LUẬT THÉP BẮT BUỘC PHẢI TUÂN THỦ
                    1. CHỐNG ẢO GIÁC: Chỉ nhắc đến tên cầu thủ có trong kết quả của Tool.
                    2. XỬ LÝ LỖI: Nếu Tool trả về rỗng, hãy phân tích dựa trên chiến thuật chung của đội thay vì cầu thủ cụ thể.
                    3. NGÔN NGỮ HỌC THUẬT VÀ SẠCH: Tuyệt đối KHÔNG sử dụng các từ ngữ liên quan đến cá độ, đặt cược, tỷ lệ kèo, nhà cái. Báo cáo thuần túy phục vụ chuyên môn thể thao.
                    4. YÊU CẦU ĐỘ DÀI: Văn phong phải mang tính báo chí phân tích thể thao (như The Athletic). Viết câu dài, lập luận nhiều lớp, mở rộng các luồng suy nghĩ. Toàn bộ báo cáo phải dài tối thiểu 1000 - 1200 chữ.
                    """
                try:
                    response = agent_executor.invoke({"input": agent_task})
                    st.success("Phân tích hoàn tất!")
                    with st.expander(f"Báo Cáo Phân Tích: {home_team} vs {away_team}", expanded=True):
                        st.markdown(response["output"])
                except Exception as e:
                    st.error(f"Lỗi AI: {str(e)}")

# ==========================================
# 8. TRUY VẤN QUA AI (MCP BRIDGE)
# ==========================================
st.divider()
with tab2:
    st.header("Truy vấn dữ liệu")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt_input := st.chat_input("VD: Lịch sử đấu của Man United 5 trận gần nhất"):
        if not openrouter_key:
            st.warning("Nhập OpenRouter API Key ở Sidebar để chat.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt_input})
            with st.chat_message("user"):
                st.markdown(prompt_input)

            with st.chat_message("assistant"):
                with st.spinner("Đang tư duy và truy vấn dữ liệu..."):
                    try:
                        agent_executor = get_agent_executor(model_choice, openrouter_key)
                        response = agent_executor.invoke({"input": prompt_input})
                        answer = response["output"]
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Lỗi kết nối API: {str(e)}")

# ==========================================
# 9. FOOTER
# ==========================================
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>Dữ liệu được cập nhật tự động | EPL Prediction Engine 2026</div>", unsafe_allow_html=True)