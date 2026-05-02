
# 1. Nhóm Đặc trưng Thời gian & Bối cảnh (Temporal Features)
Giúp mô hình nhận diện tính chu kỳ của mùa giải và áp lực tâm lý theo thời gian.

## Season (Mùa giải):

Cách tính: Dựa trên tháng của ngày thi đấu. Nếu Month >= 8, mùa giải là Year-(Year+1), ngược lại là (Year-1)-Year.

Ý nghĩa: Phân loại dữ liệu theo từng năm thi đấu để reset các chỉ số cộng dồn.

## Matchweek (Vòng đấu):

Cách tính: Số trận đấu tối đa mà hai đội đã chơi trong mùa giải hiện tại cộng thêm 1. Xử lý linh hoạt cho cả các trận đá bù.

Ý nghĩa: Xác định giai đoạn (Khởi đầu, Giữa mùa, Nước rút vòng 30+).

## Month Sin/Cos (Chu kỳ tháng):

Cách tính: np.sin/cos(2 * np.pi * Month / 12).

Ý nghĩa: Giúp mô hình hiểu giá trị tháng 12 và tháng 1 có tính chất gần nhau (giai đoạn mùa đông bận rộn).

# 2. Nhóm Đặc trưng Sức mạnh & Thứ hạng (Strength & Ranking)

Định lượng trình độ và vị thế tương quan giữa hai đối thủ trước giờ bóng lăn.

## Hệ thống điểm Elo:

Cách tính: Khởi điểm 1500 điểm. Cập nhật sau mỗi trận dựa trên kết quả thực tế vs xác suất mong đợi (K=30, lợi thế sân nhà 100 điểm).

Features: Home_Elo, Away_Elo, Elo_Diff.

## Vị trí bảng xếp hạng (League Rank):

Cách tính: BXH ảo cập nhật liên tục dựa trên Điểm > Hiệu số > Bàn thắng. Rank được lấy trước khi trận đấu diễn ra.

Features: Home_Rank, Away_Rank, Rank_Diff.

# 3. Nhóm Đặc trưng Lăn (Rolling Features - Window = 5)

Sử dụng giá trị trung bình của 5 trận gần nhất để nắm bắt phong độ tức thời.

Nhóm chỉ số (Home/Away)

## Tấn công

Avg_goals, Avg_shots, Avg_shots_ot, Avg_corners.

## Phòng ngự

Avg_goals_conceded, Avg_shots_ot_conceded.

## Kỷ luật

Avg_fouls, Avg_yellows, Avg_reds.

# 4. Nhóm Đặc trưng Hiệu suất & Áp lực (Efficiency & Pressure)

Các chỉ số phái sinh mô tả chiều sâu lối chơi của đội bóng.

    Shot Efficiency (Hiệu quả dứt điểm): Avg_shots_ot_5 / Avg_shots_5. Khả năng biến cú sút thành tình huống nguy hiểm.

    Defense Ratio (Hệ số phòng ngự): Avg_goals_conceded_5 / Avg_shots_ot_conceded_5. Khả năng ngăn chặn bàn thua khi bị sút trúng đích.

    Attack Pressure (Áp lực tấn công): (Avg_shots_ot_5 * 0.7) + (Avg_corners_5 * 0.3). Đo lường mức độ dồn ép đối phương.


# 5. Nhóm Đặc trưng Đối đầu & Duyên nợ (Aggression & H2H)

Nhóm quan trọng nhất để dự đoán thẻ phạt và các trận đấu "nóng".

    Lịch sử thắng thua (H2H): Home_H2H_Wins, Away_H2H_Wins, H2H_Draws tính từ năm 2005.

    Aggression Points (Điểm quyết liệt): (Fouls * 0.5) + Yellows + (Reds * 3).

    H2H Rivalry: Trung bình Total_Match_Points của 5 lần đối đầu gần nhất. Nhận diện các cặp đấu kình địch.

    Team Style Agg: Trung bình điểm Aggression của đội trong 5 trận gần nhất để xác định lối chơi "lăn xả".

# 6. Chiến lược xử lý dữ liệu (Data Strategy)

Tính toán trước trận (Pre-match): Tất cả các chỉ số (Rolling, Elo, Rank, H2H) đều được tính dựa trên dữ liệu lịch sử trước thời điểm trận đấu diễn ra để tránh Data Leakage.

## Xử lý giá trị thiếu (NaN):

Các trận đầu mùa được tính trung bình dựa trên số trận thực tế có sẵn (min_periods=1).

Các trận đấu trong tương lai được lấp đầy bằng global_mean (trung bình toàn giải) cho các chỉ số Aggression để Pipeline không bị ngắt quãng.