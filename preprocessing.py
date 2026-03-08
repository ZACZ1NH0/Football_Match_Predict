import pandas as pd
import glob
import os

# 1. Lấy danh sách file
path = '/workspaces/Football_Match_Predict/data' 
all_files = glob.glob(os.path.join(path, "*.csv"))

# 2. Hàm định nghĩa thứ tự ưu tiên cho mùa giải
def season_sort_key(filename):
    # Lấy tên file bỏ đuôi .csv (ví dụ: '9899')
    name = os.path.basename(filename).replace('.csv', '')
    # Lấy 2 chữ số đầu tiên làm mốc (98)
    start_year_short = int(name[:2])
    
    # Quy tắc: Nếu > 50 thì thuộc thế kỷ 20 (19xx), ngược lại là thế kỷ 21 (20xx)
    if start_year_short > 50:
        return 1900 + start_year_short
    else:
        return 2000 + start_year_short

# 3. Sắp xếp danh sách file dựa trên hàm trên
all_files.sort(key=season_sort_key)

# 4. Tiến hành gộp file
li = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0, encoding='utf-8')
    # Giữ lại các cột bạn cần
    target_columns = ['Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','HTHG','HTAG','HTR','Referee','HS','AS','HST','AST','HF','AF','HC','AC','HY','AY','HR','AR']
    # Một số file cũ có thể thiếu cột, dùng reindex để bù NaN nếu thiếu
    df = df.reindex(columns=target_columns)
    df['Season'] = os.path.basename(filename).replace('.csv', '')
    li.append(df)

full_df = pd.concat(li, axis=0, ignore_index=True)

# 5. Xử lý cột Date sau khi gộp để đảm bảo tuyệt đối về thứ tự

full_df['Date'] = pd.to_datetime(full_df['Date'], dayfirst=True, errors='coerce')
full_df = full_df.sort_values(by='Date').reset_index(drop=True)

print("Thứ tự các mùa giải sau khi gộp:")
print(full_df['Season'].unique())

full_df.to_csv("full.csv")