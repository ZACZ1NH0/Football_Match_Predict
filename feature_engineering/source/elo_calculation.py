import pandas as pd
import numpy as np

def calculate_elo(df, k_factor=30, home_advantage=100):
    # 1. Khởi tạo dictionary lưu điểm ELO hiện tại của các đội
    # Mặc định mỗi đội là 1500
    all_teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
    elo_ratings = {team: 1500 for team in all_teams}
    
    # Danh sách để lưu ELO TRƯỚC trận đấu (để đưa vào Feature)
    home_elo_before = []
    away_elo_before = []
    
    # Duyệt qua từng trận đấu theo thứ tự thời gian
    for idx, row in df.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        result = row['FTR']
        
        # Lấy điểm ELO hiện tại
        r_h = elo_ratings[home_team]
        r_a = elo_ratings[away_team]
        
        # Lưu lại điểm TRƯỚC trận để làm Feature dự đoán
        home_elo_before.append(r_h)
        away_elo_before.append(r_a)
        
        # 2. Tính toán xác suất mong đợi (Expected Score)
        # Có tính đến lợi thế sân nhà (home_advantage)
        e_h = 1 / (1 + 10 ** ((r_a - (r_h + home_advantage)) / 400))
        e_a = 1 - e_h
        
        # 3. Xác định kết quả thực tế (Actual Score)
        if result == 'H':
            s_h, s_a = 1, 0
        elif result == 'A':
            s_h, s_a = 0, 1
        else: # Hòa
            s_h, s_a = 0.5, 0.5
            
        # 4. Cập nhật điểm ELO sau trận đấu
        elo_ratings[home_team] = r_h + k_factor * (s_h - e_h)
        elo_ratings[away_team] = r_a + k_factor * (s_a - e_a)
        
    # Thêm vào dataframe chính
    df['Home_Elo'] = home_elo_before
    df['Away_Elo'] = away_elo_before
    df['Elo_Diff'] = df['Home_Elo'] - df['Away_Elo']
    
    return df, elo_ratings
