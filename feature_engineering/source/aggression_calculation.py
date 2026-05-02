import numpy as np
import pandas as pd

def calculate_advanced_aggression(df):
    data = df.copy()
    
    # 1. Tính điểm Aggression (Chỉ những trận đã có dữ liệu thẻ phạt)
    # Dùng fillna(0) để các trận tương lai không làm hỏng phép tính mean() sau này
    data['Home_Points'] = (data['HF'].fillna(0) * 0.5) + data['HY'].fillna(0) + (data['HR'].fillna(0) * 3)
    data['Away_Points'] = (data['AF'].fillna(0) * 0.5) + data['AY'].fillna(0) + (data['AR'].fillna(0) * 3)
    data['Total_Match_Points'] = data['Home_Points'] + data['Away_Points']

    # Tính giá trị trung bình toàn giải (chỉ tính trên các trận đã đá)
    # Lấy những trận mà FTR không phải None/NaN
    past_matches = data[data['FTR'].notna()]
    global_mean_total = past_matches['Total_Match_Points'].mean()
    global_mean_home = past_matches['Home_Points'].mean()
    global_mean_away = past_matches['Away_Points'].mean()

    def get_features(row):
        home, away, date = row['HomeTeam'], row['AwayTeam'], row['Date']
        
        # --- Phần 1: H2H Rivalry ---
        h2h = data[
            ((data['HomeTeam'] == home) & (data['AwayTeam'] == away) |
             (data['HomeTeam'] == away) & (data['AwayTeam'] == home)) &
            (data['Date'] < date)
        ].sort_values('Date', ascending=False).head(5)
        
        # Nếu không có H2H, dùng trung bình toàn giải của các trận ĐÃ ĐÁ
        h2h_idx = h2h['Total_Match_Points'].mean() if not h2h.empty else global_mean_total

        # --- Phần 2: Team Style ---
        def calc_team_pts(team, current_date, default_val):
            recent = data[
                ((data['HomeTeam'] == team) | (data['AwayTeam'] == team)) & 
                (data['Date'] < current_date) &
                (data['FTR'].notna()) # QUAN TRỌNG: Chỉ lấy phong độ từ các trận đã kết thúc
            ].sort_values('Date', ascending=False).head(5)
            
            pts = []
            for _, r in recent.iterrows():
                pts.append(r['Home_Points'] if r['HomeTeam'] == team else r['Away_Points'])
            return np.mean(pts) if pts else default_val

        home_style = calc_team_pts(home, date, global_mean_home)
        away_style = calc_team_pts(away, date, global_mean_away)

        return pd.Series([h2h_idx, home_style, away_style])

    # Thực hiện apply
    data[['H2H_Rivalry', 'Home_Style_Agg', 'Away_Style_Agg']] = data.apply(get_features, axis=1)
    return data