def shot_and_defense(full_df):
    # 1. Shot Efficiency (Hiệu quả dứt điểm - Tấn công)
    full_df['Home_Shot_Efficiency'] = full_df['Home_Avg_shots_ot_5'] / (full_df['Home_Avg_shots_5'] + 1e-5)
    full_df['Away_Shot_Efficiency'] = full_df['Away_Avg_shots_ot_5'] / (full_df['Away_Avg_shots_5'] + 1e-5)

    # 2. Defense Factor (Hệ số phòng ngự)
    # Lưu ý: "Home_Avg_goals_conceded_5" là số bàn thua
    # Chúng ta cần chia cho số cú sút trúng đích mà ĐỐI THỦ gây ra (đã được tính trong hàm rolling)
    full_df['Home_Defense_Ratio'] = full_df['Home_Avg_goals_conceded_5'] / (full_df['Home_Avg_shots_ot_conceded_5'] + 1e-5)
    full_df['Away_Defense_Ratio'] = full_df['Away_Avg_goals_conceded_5'] / (full_df['Away_Avg_shots_ot_conceded_5'] + 1e-5)

    # 3. Pressure Index (Chỉ số áp lực - Kết hợp Phạt góc)
    full_df['Home_Attack_Pressure'] = (full_df['Home_Avg_shots_ot_5'] * 0.7) + (full_df['Home_Avg_corners_5'] * 0.3)
    full_df['Away_Attack_Pressure'] = (full_df['Away_Avg_shots_ot_5'] * 0.7) + (full_df['Away_Avg_corners_5'] * 0.3)

    return full_df