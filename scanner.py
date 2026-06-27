import pandas as pd
import yfinance as yf
import logging
import concurrent.futures
from threading import Lock
from utils import check_gold_silver_pattern, check_resistance, get_capital_billion

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

results_lock = Lock()
results = []

def process_ticker(ticker):
    try:
        # 1. 取得股本資訊
        cap = get_capital_billion(ticker)
        if cap is None or cap > 150: return

        # 2. 下載日線資料
        data_day = yf.download(ticker, period="1y", interval="1d", progress=False)
        if isinstance(data_day.columns, pd.MultiIndex):
            data_day.columns = data_day.columns.get_level_values(0)
        if len(data_day) < 120: return

        current_volume = data_day['Volume'].iloc[-1]
        if pd.isna(current_volume): current_volume = 0
        if current_volume < 500_000: return

        # 3. 基礎壓力與趨勢確認
        price = float(data_day['Close'].iloc[-1])
        resistance_status, resistance_dist = check_resistance(price, data_day)

        # 4. 下載 60 分鐘線並檢查金包銀型態
        # 將週期改為 3mo 以確保有足夠資料計算 240MA
        data_60m = yf.download(ticker, period="3mo", interval="60m", progress=False)
        if isinstance(data_60m.columns, pd.MultiIndex):
            data_60m.columns = data_60m.columns.get_level_values(0)
        
        # 使用新的金包銀邏輯
        if check_gold_silver_pattern(data_60m):
            with results_lock:
                results.append({
                    "Ticker": ticker, 
                    "股本(億)": round(cap, 2), 
                    "成交量(張)": int(current_volume / 1000),
                    "型態": "金包銀✅",
                    "壓力狀態": resistance_status,
                    "距壓力%": resistance_dist
                })
            print(f"--> 找到金包銀標的: {ticker} | 成交量: {int(current_volume/1000)}張 | 狀態: {resistance_status}")
            
    except Exception as e:
        pass

def run_scanner():
    try:
        tickers = pd.read_csv('small_cap_list.csv')['Ticker'].tolist()
    except FileNotFoundError:
        print("錯誤：找不到 small_cap_list.csv")
        return

    print(f"啟動金包銀掃描引擎，共 {len(tickers)} 檔...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(process_ticker, tickers)
            
    if results:
        pd.DataFrame(results).to_csv('results.csv', index=False, encoding='utf-8-sig')
        print(f"掃描完成！共找到 {len(results)} 檔，結果存入 results.csv")
    else:
        print("掃描完成，未找到符合金包銀條件的標的。")

if __name__ == "__main__":
    run_scanner()