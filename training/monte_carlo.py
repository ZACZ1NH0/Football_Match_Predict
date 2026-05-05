import pandas as pd
import numpy as np
from tqdm import tqdm

def run_monte_carlo(df_probs, n_simulations=10000):
    all_sim_results = []
    teams = pd.concat([df_probs['HomeTeam'], df_probs['AwayTeam']]).unique()
    
    for _ in tqdm(range(n_simulations), desc="Simulating Season"):
        # Tạo bảng điểm trống cho mỗi simulation
        points = {team: 0 for team in teams}
        
        # Duyệt qua từng trận đấu
        for _, row in df_probs.iterrows():
            # Tung xúc xắc ngẫu nhiên dựa trên xác suất
            res = np.random.choice(['H', 'D', 'A'], p=[row['Home_Prob'], row['Draw_Prob'], row['Away_Prob']])
            
            if res == 'H':
                points[row['HomeTeam']] += 3
            elif res == 'D':
                points[row['HomeTeam']] += 1
                points[row['AwayTeam']] += 1
            else:
                points[row['AwayTeam']] += 3
                
        all_sim_results.append(points)
    
    # Tổng hợp kết quả từ 10,000 lần chạy
    sim_df = pd.DataFrame(all_sim_results)
    
    # Tính điểm trung bình, max, min cho mỗi đội
    final_table = pd.DataFrame({
        'Team': teams,
        'Avg_Points': [sim_df[team].mean() for team in teams],
        'Max_Points': [sim_df[team].max() for team in teams],
        'Min_Points': [sim_df[team].min() for team in teams],
        'Win_Title_Prob': [(sim_df[team] == sim_df.max(axis=1)).mean() * 100 for team in teams]
    })
    
    return final_table.sort_values(by='Avg_Points', ascending=False)
