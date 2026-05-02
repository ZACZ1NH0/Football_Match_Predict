def add_h2h_features(df):
    h2h_map = {} 
    
    h2h_home_wins = []
    h2h_away_wins = []
    h2h_draws = []
    
    for idx, row in df.iterrows():
        # Đảm bảo tên đội luôn được sắp xếp để tạo key duy nhất cho cặp đối đầu
        teams = tuple(sorted([row['HomeTeam'], row['AwayTeam']]))
        team_h = row['HomeTeam']
        team_a = row['AwayTeam']
        
        # Khởi tạo nếu cặp đội này lần đầu xuất hiện
        if teams not in h2h_map:
            h2h_map[teams] = {team_h: 0, team_a: 0, 'draw': 0}
        # Trường hợp đặc biệt: Đội mới thăng hạng có thể chưa có key trong dict con
        if team_h not in h2h_map[teams]: h2h_map[teams][team_h] = 0
        if team_a not in h2h_map[teams]: h2h_map[teams][team_a] = 0
        
        # 1. LẤY DỮ LIỆU LỊCH SỬ (Trước khi trận này diễn ra)
        # Đây là dữ liệu Model sẽ dùng để dự đoán
        current_h2h = h2h_map[teams]
        h2h_home_wins.append(current_h2h.get(team_h, 0))
        h2h_away_wins.append(current_h2h.get(team_a, 0))
        h2h_draws.append(current_h2h['draw'])
        
        # 2. CHỈ CẬP NHẬT KẾT QUẢ NẾU TRẬN ĐẤU ĐÃ CÓ KẾT QUẢ
        # Dùng pd.notna() để bỏ qua các trận tuần tới (FTR = NaN)
        if pd.notna(row['FTR']):
            if row['FTR'] == 'H':
                h2h_map[teams][team_h] += 1
            elif row['FTR'] == 'A':
                h2h_map[teams][team_a] += 1
            elif row['FTR'] == 'D': # Ghi rõ 'D' cho chắc chắn
                h2h_map[teams]['draw'] += 1
            
    df['Home_H2H_Wins'] = h2h_home_wins
    df['Away_H2H_Wins'] = h2h_away_wins
    df['H2H_Draws'] = h2h_draws
    return df