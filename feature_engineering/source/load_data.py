import pandas as pd

from feature_engineering.source.get_comming_up_match import get_upcoming_fixtures


def load_data():
    SEASONS = {
        # '2000-01': '0001',
        # '2001-02': '0102',
        # '2002-03': '0203',
        # '2003-04': '0304',
        # '2004-05': '0405',
        '2005-06': '0506',
        '2006-07': '0607',
        '2007-08': '0708',
        '2008-09': '0809',
        '2009-10': '0910',
        '2010-11': '1011',
        '2011-12': '1112',
        '2012-13': '1213',
        '2013-14': '1314',
        '2014-15': '1415',
        '2015-16': '1516',
        '2016-17': '1617',
        '2017-18': '1718',
        '2018-19': '1819',
        '2019-20': '1920',
        '2020-21': '2021',
        '2021-22': '2122',
        '2022-23': '2223',
        '2023-24': '2324',
        '2024-25': '2425',
        '2025-26': '2526'
    }

    BASE_URL = 'https://www.football-data.co.uk/mmz4281/{code}/E0.csv'

    COLS = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR',
            'HS', 'AS', 'HY', 'AY', 'HST', 'AST', 'HC', 'AC', 'HR', 'AR', 'HF', 'AF' ]

    print("Loading data from Football-Data.co.uk...\n")
    dfs = []
    for season_name, season_code in SEASONS.items():
        url = BASE_URL.format(code=season_code)
        try:
            df = pd.read_csv(url, encoding='utf-8')
            available_cols = [c for c in COLS if c in df.columns]
            df = df[available_cols].copy()
            df['Season'] = season_name
            print(f"  {season_name}: {len(df)} matches")
            dfs.append(df)
        except Exception as e:
            print(f"  {season_name}: Failed - {e}")

    df = pd.concat(dfs, ignore_index=True)
    df = df.dropna(subset=['Date', 'HomeTeam'])
    try:
        # Gọi hàm lấy Fixtures mà chúng ta vừa viết (đảm bảo hàm này đã được định nghĩa trước)
        df_upcoming = get_upcoming_fixtures(football_api_key) 
        
        if not df_upcoming.empty:
            # df_upcoming = df_upcoming.sort_values('Date')
            df_upcoming = df_upcoming.head(10)
            
            team_mapping = {
                'Nottingham': "Nott'm Forest", 'Brighton Hove': 'Brighton',
                'Leeds United': 'Leeds', 'Wolverhampton': 'Wolves'
                # Kiểm tra lại tên chuẩn trong CSV của bạn
            }
            df_upcoming['HomeTeam'] = df_upcoming['HomeTeam'].replace(team_mapping)
            df_upcoming['AwayTeam'] = df_upcoming['AwayTeam'].replace(team_mapping)
            
            # Nối vào df chính
            df = pd.concat([df, df_upcoming], ignore_index=True)
            print(f"\n✅ Added {len(df_upcoming)} upcoming fixtures from API.")
    except Exception as e:
        print(f"\n⚠️ Could not add API fixtures: {e}")

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.sort_values('Date').reset_index(drop=True)

    print(f"\nTotal matches: {len(df)}")
    print(f"Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    return df