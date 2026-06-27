import streamlit as st
import pandas as pd
import yfinance as yf
import os
from datetime import datetime

# 從 utils.py 匯入你剛定義好的功能
from utils import check_gold_silver_pattern, get_capital_billion

# --- 設定頁面 ---
st.set_page_config(page_title="金包銀選股雷達", layout="wide")

# --- UI 介面 ---
st.title("金包銀選股雷達 📊")
tab1, tab2 = st.tabs(["單檔即時診斷", "全場掃描結果"])

with tab1:
    st.subheader("單檔即時診斷")
    ticker_input = st.text_input("請輸入股票代號 (例如: 2330):")
    
    if st.button("進行診斷"):
        if ticker_input:
            with st.spinner('正在分析中...'):
                ticker = ticker_input.strip()
                
                # 自動判斷加上 .TW 或 .TWO (預設先試原代號)
                possible_tickers = [ticker, f"{ticker}.TW", f"{ticker}.TWO"]
                df_day, valid_ticker = None, None
                
                for t in possible_tickers:
                    temp_day = yf.download(t, period="1y", interval="1d", progress=False)
                    if not temp_day.empty:
                        if isinstance(temp_day.columns, pd.MultiIndex):
                            temp_day.columns = temp_day.columns.get_level_values(0)
                        df_day = temp_day
                        valid_ticker = t
                        break
                
                if df_day is not None:
                    # 1. 取得市值資訊
                    cap = get_capital_billion(valid_ticker)
                    
                    # 2. 下載 60 分鐘線進行金包銀檢測
                    df_60m = yf.download(valid_ticker, period="3mo", interval="60m", progress=False)
                    if isinstance(df_60m.columns, pd.MultiIndex): 
                        df_60m.columns = df_60m.columns.get_level_values(0)
                    
                    # 3. 使用金包銀邏輯
                    is_pattern = check_gold_silver_pattern(df_60m)
                    
                    # 4. 顯示結果
                    st.write(f"### 診斷標的: {valid_ticker}")
                    col1, col2 = st.columns(2)
                    col1.metric("市值 < 150億", "✅ 符合" if cap and cap < 150 else "❌ 超標")
                    col2.metric("金包銀型態", "✅ 符合" if is_pattern else "❌ 未符合")
                    
                    # 顯示近期走勢圖
                    st.line_chart(df_day['Close'].tail(100))
                else:
                    st.error(f"找不到代號 {ticker}，請確認輸入是否正確。")

with tab2:
    st.subheader("全場掃描結果")
    file_path = 'results.csv'
    
    if os.path.exists(file_path):
        mtime = os.path.getmtime(file_path)
        last_updated = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        st.info(f"🕒 數據最後更新時間: {last_updated}")
        
        df = pd.read_csv(file_path)
        st.dataframe(df, use_container_width=True)
        
        st.download_button(
            label="📥 下載完整結果 (CSV)",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name='results.csv',
            mime='text/csv'
        )
    else:
        st.warning("找不到 results.csv，請確認掃描程式 (scanner.py) 是否已成功執行。")
    
    if st.button("重新整理資料"):
        st.rerun()