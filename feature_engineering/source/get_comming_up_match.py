import requests
import pandas as pd

def get_upcoming_fixtures(api_key):
    # Endpoint lấy các trận đấu của Premier League (Mã giải đấu là 'PL' hoặc ID 2021)
    url = "https://api.football-data.org/v4/competitions/PL/matches?status=SCHEDULED"
    headers = { 'X-Auth-Token': api_key }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        fixtures = []
        for match in data['matches']:
            fixtures.append({
                'Date': match['utcDate'],
                'HomeTeam': match['homeTeam']['shortName'], # Hoặc .name tùy theo mapping
                'AwayTeam': match['awayTeam']['shortName'],
                'Season': '2025-26',
                'FTR': None # Trận chưa đá nên kết quả để trống
            })
            
        df_fixtures = pd.DataFrame(fixtures)
        # Chuyển đổi Date sang datetime và bỏ phần giờ để khớp với CSV
        df_fixtures['Date'] = pd.to_datetime(df_fixtures['Date']).dt.tz_localize(None)
        
        return df_fixtures
    
    except Exception as e:
        print(f"❌ Lỗi khi lấy API: {e}")
        return pd.DataFrame()