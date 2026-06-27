import pandas as pd
import requests
import io
import os

def fetch_stock_list():
    print("正在從證交所下載最新股票清單...")
    headers = {'user-agent': 'Mozilla/5.0'}
    
    # 這裡加入 strMode=2 (上市) 與 strMode=4 (上櫃)
    urls = [
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2",
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
    ]
    
    all_dfs = []
    
    for url in urls:
        try:
            res = requests.get(url, headers=headers)
            res.encoding = 'big5'
            dfs = pd.read_html(io.StringIO(res.text))
            df = dfs[0]
            
            # 定位標題列
            header_idx = df[df.apply(lambda row: row.astype(str).str.contains('有價證券代號及名稱').any(), axis=1)].index[0]
            df.columns = df.iloc[header_idx]
            df = df.iloc[header_idx + 1:]
            df.columns = df.columns.str.strip()
            
            # 整理欄位
            df = df.rename(columns={'有價證券代號及名稱': 'Symbol_Name', '市場別': 'Market'})
            split_df = df['Symbol_Name'].str.split(n=1, expand=True)
            df['Code'] = split_df[0].str.strip()
            df['Name'] = split_df[1].str.strip()
            df['Market'] = df['Market'].str.strip()
            
            all_dfs.append(df)
            print(f"成功抓取一組資料: {url.split('=')[-1]}")
            
        except Exception as e:
            print(f"下載失敗: {e}")
            continue

    # 合併兩份資料
    df = pd.concat(all_dfs, ignore_index=True)
    print(f"合併後原始總數: {len(df)}")

    # 篩選條件
    df = df[df['Market'].isin(['上市', '上櫃'])].copy()
    df = df[(df['Code'].str.len() == 4) & (df['Code'].str.isdigit())]

    # 黑名單機制
    if os.path.exists('blacklist.txt'):
        with open('blacklist.txt', 'r', encoding='utf-8') as f:
            blacklist = [line.strip() for line in f if line.strip()]
        df = df[~df['Code'].isin(blacklist)]
        print(f"已排除黑名單，剔除 {len(blacklist)} 檔。")

    # 剔除 ETF、特別股等
    exclude_keywords = ['ETF', '認購', '認售', '特別股', '存託', 'ETN']
    for keyword in exclude_keywords:
        df = df[~df['Name'].str.contains(keyword, na=False)]
    
    # 輸出：上市加 .TW，上櫃加 .TWO
    def format_ticker(row):
        return f"{row['Code']}.TW" if row['Market'] == '上市' else f"{row['Code']}.TWO"
        
    df['Ticker'] = df.apply(format_ticker, axis=1)
    
    output = df[['Ticker', 'Code', 'Name', 'Market']]
    output.to_csv('small_cap_list.csv', index=False, encoding='utf-8-sig')
    print(f"清單更新完成！最終保留 {len(output)} 檔股票。")

if __name__ == "__main__":
    fetch_stock_list()