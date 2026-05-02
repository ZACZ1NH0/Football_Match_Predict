import pandas as pd

def create_rolling_features(df, n_games=5):
    # Đảm bảo sắp xếp theo thời gian
    data = df.sort_values('Date').copy()
    
    # Danh sách các chỉ số thô cần tính rolling
    metrics = {
        'goals': ['FTHG', 'FTAG'],
        'shots': ['HS', 'AS'],
        'shots_ot': ['HST', 'AST'],
        'corners': ['HC', 'AC'],
        'fouls': ['HF', 'AF'],
        'yellows': ['HY', 'AY'],
        'reds': ['HR', 'AR']
    }

    # Khởi tạo các cột kết quả với NaN
    for side in ['Home', 'Away']:
        for m in metrics.keys():
            data[f'{side}_Avg_{m}_{n_games}'] = np.nan
            data[f'{side}_Avg_{m}_Conceded_{n_games}'] = np.nan

    all_teams = pd.concat([data['HomeTeam'], data['AwayTeam']]).unique()

    for team in all_teams:
        # Lọc các trận của đội này
        team_mask = (data['HomeTeam'] == team) | (data['AwayTeam'] == team)
        team_df = data[team_mask].copy()
        
        # 1. Tạo một DataFrame TẠM THỜI chỉ chứa các con số để tính Rolling
        # Không đưa cột 'Date' vào đây
        rows = []
        for idx, row in team_df.iterrows():
            is_home = row['HomeTeam'] == team
            stats = {
                'goals': row['FTHG'] if is_home else row['FTAG'],
                'goals_conceded': row['FTAG'] if is_home else row['FTHG'],
                'shots': row['HS'] if is_home else row['AS'],
                'shots_conceded': row['AS'] if is_home else row['HS'], # Thêm cái này
                'shots_ot': row['HST'] if is_home else row['AST'],
                'shots_ot_conceded': row['AST'] if is_home else row['HST'], # VÀ CÁI NÀY
                'corners': row['HC'] if is_home else row['AC'],
                'fouls': row['HF'] if is_home else row['AF'],
                'yellows': row['HY'] if is_home else row['AY'],
                'reds': row['HR'] if is_home else row['AR']
            }
            rows.append(stats)
        
        # Tạo df chỉ gồm số, reset index để tránh lỗi Date ở Index
        temp_stats_df = pd.DataFrame(rows, index=team_df.index)
        
        # 2. Tính Rolling trên dữ liệu THUẦN SỐ
        roll_df = temp_stats_df.shift(1).rolling(window=n_games, min_periods=1).mean()
        
        # 3. Gán ngược lại vào DataFrame chính dựa trên Index
       # 3. Gán ngược lại vào DataFrame chính dựa trên Index
        for idx in team_df.index:
            is_home = data.at[idx, 'HomeTeam'] == team
            prefix = 'Home' if is_home else 'Away'
            
            # Gán toàn bộ các chỉ số đã tính trong roll_df
            for col in temp_stats_df.columns:
                # col ở đây bao gồm: goals, goals_conceded, shots, shots_ot, corners, ...
                if 'conceded' in col:
                    # Gán các chỉ số phòng ngự: shots_ot_conceded, goals_conceded...
                    data.at[idx, f'{prefix}_Avg_{col}_{n_games}'] = roll_df.at[idx, col]
                else:
                    # Gán các chỉ số tấn công: shots, shots_ot, corners...
                    data.at[idx, f'{prefix}_Avg_{col}_{n_games}'] = roll_df.at[idx, col]
            
            # QUAN TRỌNG: Để tính Defense_Ratio, chúng ta cần shots_ot bị đối phương sút
            # Trong stats ở bước 1, bạn chưa tính 'shots_ot_conceded'. Hãy thêm nó vào bước 1!
    return data