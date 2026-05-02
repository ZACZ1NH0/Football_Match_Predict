# Nguồn dữ liệu: 

https://datahub.io/core/english-premier-league 
https://www.football-data.co.uk/englandm.php

### api next match
https://www.football-data.org/

# Data description

## 1. Thông tin trận đấu (Metadata)

Đây là các biến định danh, dùng để phân nhóm hoặc làm khóa (key) để nối các bảng dữ liệu khác.

    Date: Ngày diễn ra. Trong CS, cần convert sang datetime. Nó giúp tính toán "Rest Days" (số ngày nghỉ giữa các trận) — một biến cực kỳ quan trọng ảnh hưởng đến thể lực.

    HomeTeam / AwayTeam: Tên đội nhà/đội khách. Đây là biến định danh (Categorical), dùng chúng để tính phong độ lịch sử của từng đội.

## 2. Kết quả mục tiêu (Target Variables)

    FTHG / FTAG: (Full Time Home/Away Goals) Số bàn thắng cả trận. 

    FTR: (Full Time Result) Kết quả cuối cùng (H: Chủ thắng, D: Hòa, A: Khách thắng). Đây là nhãn (Label) phổ biến nhất cho bài toán Classification.

## 3. Chỉ số hiệu suất tấn công (Performance Features)
Những con số này phản ánh "thế trận" thực sự hơn là chỉ nhìn vào bàn thắng.

    HS / AS: (Home/Away Shots) Tổng số cú sút. Phản ánh độ chủ động tấn công.

    HST / AST: (Home/Away Shots on Target) Sút trúng đích. Đây là chỉ số "vàng" vì nó có tương quan (correlation) rất cao với bàn thắng thực tế.

    HC / AC: (Home/Away Corners) Phạt góc. Thường dùng để đo sức ép mà một đội tạo ra lên phần sân đối phương.

## 4. Chỉ số kỷ luật và lối chơi (Disciplinary Features)

Giúp mô hình hiểu được lối chơi của đội bóng (phòng ngự tiêu cực, đá rát, hay kỷ luật).

    HF / AF: (Home/Away Fouls) Số lỗi phạm phải.

    HY / AY: (Home/Away Yellow Cards) Thẻ vàng.

    HR / AR: (Home/Away Red Cards) Thẻ đỏ. Lưu ý: Một chiếc thẻ đỏ sớm có thể làm nhiễu (outlier) kết quả trận đấu, khiến các chỉ số tấn công khác không còn phản ánh đúng thực lực.
