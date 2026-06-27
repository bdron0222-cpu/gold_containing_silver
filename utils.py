import pandas as pd
import yfinance as yf

def check_gold_silver_pattern(df):
    """
    金包銀策略檢測 (較寬鬆版本)
    - 60分K線，資料需滿 240 根
    - 壓力區確認：240MA & 120MA > Price
    - 短線發動區：MA5, MA10 皆 < 60MA
    - 趨勢確認：MA5, MA10 呈現上彎 (當期 > 前期)
    """
    if df.empty or len(df) < 240: 
        return False
    
    # 計算 MA 的輔助函數
    def get_ma(n):
        ma = df['Close'].rolling(window=n).mean()
        return ma.iloc[-1], ma.iloc[-2]

    curr_price = df['Close'].iloc[-1]
    
    # 計算均線 (當期與前期)
    ma240_c, _ = get_ma(240)
    ma120_c, _ = get_ma(120)
    ma60_c, _ = get_ma(60)
    ma10_c, ma10_p = get_ma(10)
    ma5_c, ma5_p = get_ma(5)

    # 1. 壓力空間確認 (上方需有壓力)
    if not (ma240_c > curr_price and ma120_c > curr_price):
        return False

    # 2. 短線發動區確認 (寬鬆：只要 MA5, MA10 在 60MA 下方即可)
    if not (ma5_c < ma60_c and ma10_c < ma60_c):
        return False

    # 3. 趨勢確認 (寬鬆：MA5, MA10 上彎)
    if not (ma5_c > ma5_p and ma10_c > ma10_p):
        return False

    return True

def check_resistance(price, data_day):
    """
    計算壓力狀態
    """
    price = float(price)
    ma_periods = [20, 60, 120]
    mas = {p: float(data_day['Close'].rolling(window=p).mean().iloc[-1]) for p in ma_periods}
    mas_above = {p: val for p, val in mas.items() if val > price}
    
    if not mas_above: 
        return "無明顯阻力", 0.0
    
    min_dist = min([(val - price) / price * 100 for val in mas_above.values()])
    
    if min_dist < 0.5: 
        return "壓力臨近(危險)", round(min_dist, 2)
    elif min_dist < 1.5: 
        return "有壓力空間尚可", round(min_dist, 2)
    else: 
        return "有壓力但空間足夠", round(min_dist, 2)

def get_capital_billion(ticker_yf):
    """
    取得股本資訊
    """
    try:
        stock = yf.Ticker(ticker_yf)
        shares = stock.info.get('sharesOutstanding')
        return (shares * 10) / 100_000_000 if shares else None
    except: 
        return None