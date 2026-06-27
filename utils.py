import pandas as pd
import yfinance as yf

def check_gold_silver_pattern(df):
    """
    金包銀策略檢測 (寬鬆版)
    - 60分K線
    - 240MA, 120MA > Price (上方壓力)
    - Price > 60MA (站上60MA)
    - 60MA 上彎
    - 5, 10, 20MA 皆 < 60MA (不需上彎)
    """
    if df.empty or len(df) < 240: 
        return False
    
    # 定義計算 MA 的輔助函數
    def get_ma_values(n):
        ma = df['Close'].rolling(window=n).mean()
        return ma.iloc[-1], ma.iloc[-2]

    # 計算所需的均線
    curr_price = df['Close'].iloc[-1]
    ma240_c, _ = get_ma_values(240)
    ma120_c, _ = get_ma_values(120)
    ma60_c, ma60_p = get_ma_values(60)
    ma20_c, _ = get_ma_values(20)
    ma10_c, _ = get_ma_values(10)
    ma5_c, _ = get_ma_values(5)

    # 1. 上方壓力檢查 (240MA & 120MA > Price)
    if not (ma240_c > curr_price and ma120_c > curr_price):
        return False

    # 2. 中軸檢查 (Price > 60MA 且 60MA上彎)
    if not (curr_price > ma60_c and ma60_c > ma60_p):
        return False

    # 3. 發動區檢查 (5, 10, 20MA 皆 < 60MA)
    # 這裡移除了上彎的條件判斷
    if not (ma5_c < ma60_c and ma10_c < ma60_c and ma20_c < ma60_c):
        return False

    return True

def check_resistance(price, data_day):
    price = float(price)
    ma_periods = [20, 60, 120]
    mas = {p: float(data_day['Close'].rolling(window=p).mean().iloc[-1]) for p in ma_periods}
    mas_above = {p: val for p, val in mas.items() if val > price}
    if not mas_above: return "無明顯阻力", 0.0
    min_dist = min([(val - price) / price * 100 for val in mas_above.values()])
    if min_dist < 0.5: return "壓力臨近(危險)", round(min_dist, 2)
    elif min_dist < 1.5: return "有壓力空間尚可", round(min_dist, 2)
    else: return "有壓力但空間足夠", round(min_dist, 2)

def get_capital_billion(ticker_yf):
    try:
        stock = yf.Ticker(ticker_yf)
        shares = stock.info.get('sharesOutstanding')
        return (shares * 10) / 100_000_000 if shares else None
    except: return None