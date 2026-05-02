Ta dùng streamlit load dữ liệu từ 4 sheet kết quả trận đấu, tạo dashboard chi tiết kết quả gồm bảng xếp hạng hiện tại. Danh sách kết quả 10 trận mới nhất (sắp diễn ra). Các thông tin dự đoán liên quan.

Bên dưới có bộ lọc để chọn 2 đội để xem dự đoán. Khi apply sẽ hiện ra thông tin như phong độ của mỗi đội. Lịch sử đối đầu hai đội, dự đoán từ 4 bảng (phần trăm thắng hòa , số bàn thắng, số góc, số thẻ phạt)

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

Bảng kết quả dự đoán (Đội nhà thắng, hòa, đội khách thắng)
url_results = "https://docs.google.com/spreadsheets/d/1qrbQTBuN3eSz1yDxpVQQ0r0aaGx_QhftJS5vMeIlnoA/edit?usp=sharing"

Gồm các cột: 
Date	HomeTeam	AwayTeam	Home_H2H_Wins	Away_H2H_Wins	H2H_Draws	Home_Rank	Away_Rank	Matchweek	Away_Win_Percent	Draw_Percent	Home_Win_Percent	Predict
2025-08-15	Liverpool	Bournemouth	13	2	1	1	2	1	32,52000046	33,40000153	34,09000015	H

Bảng kết quả dự đoán bàn thắng
url_goals = "https://docs.google.com/spreadsheets/d/16AsBqjf--nrUxi7ewfYkpwt7tA97EdajwZ4drGH9kck/edit?usp=sharing"

Gồm các cột 
Date	HomeTeam	AwayTeam	Home_H2H_Wins	Away_H2H_Wins	H2H_Draws	Home_Rank	Away_Rank	Matchweek	xG_Home	xG_Away	
2025-08-15	Liverpool	Bournemouth	13	2	1	1	2	1	2,00999999	1,279999971	

Bảng kết quả dự đoán số lần phạt góc của đội nhà và đội khách 
url_corners = "https://docs.google.com/spreadsheets/d/1sPlI2Dw67I82bv_0aZkzPsYG0tvmWF8mpt_ucJyZHbE/edit?usp=sharing"

Gồm các cột, ví dụ:
Date	HomeTeam	AwayTeam	Home	Away	
2025-08-15	Liverpool	Bournemouth	195,016822	5	3,589999914	

Bảng kết quả dự đoán số thẻ phạt của đội nhà và đội khách
url_yellow_card = "https://docs.google.com/spreadsheets/d/1szCjFPXYZViNPpzgbkW8Uak67CLRHCs-stos-aGd7Bk/edit?usp=sharing"

Gồm các cột, ví dụ: 
Date	HomeTeam	AwayTeam	Home	Away	
2025-08-15	Liverpool	Bournemouth	195,016822	1,669999957	1,970000029	
