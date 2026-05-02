Dữ liệu được đưa về từ link 'https://www.football-data.co.uk/mmz4281/{code}/E0.csv' 

Để dữ liệu được đầy đủ, ta sẽ lấy các mùa giải từ 2005 đến mùa giải hiện tại (2025-2026)

Các cột hiện có là: 'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR','HS', 'AS', 'HY', 'AY', 'HST', 'AST', 'HC', 'AC', 'HR', 'AR', 'HF', 'AF'

Đầu tiên ta dùng pd.concat để nối các mùa giải theo thứ tự từ quá khứ đến hiện tại.

Sau đó dùng dropna để loại bỏ những bản ghi bị thiếu. Những bản ghi này không nhiều và khi bỏ đi cũng không ảnh hưởng đến kết quả hiện tại. 

Tiếp theo ta load dữ liệu từ hàm get_comming_up_match lấy 10 trận mới nhất sắp diễn ra 
https://api.football-data.org/v4/competitions/PL/matches?status=SCHEDULED 

Date', 'HomeTeam', 'AwayTeam', 'Season' là những cột mà ta thu được. Các thông tin về kết quả trận đấu sẽ được để trống.

Vì dữ liệu lịch sử các trận trong quá khứ và dữ liệu các trận sắp diễn ra là hai bộ dữ liệu khác nhau. Nên ta cần mapping những tên đội bóng cho khớp giữa hai bộ dữ liệu.

