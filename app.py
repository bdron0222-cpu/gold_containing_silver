import streamlit as st
import pandas as pd
import yfinance as yf
import os
from datetime import datetime

# 從 utils.py 匯入功能
# 從 utils.py 匯入功能
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
            with st.spinner('連線分析中...'):
            with st.spinner('連線分析中...'):
                ticker = ticker_input.strip()
                # 自動嘗試不同後綴
                possible_targets = [ticker, f"{ticker}.TW", f"{ticker}.TWO"]
                # 自動嘗試不同後綴
                possible_targets = [ticker, f"{ticker}.TW", f"{ticker}.TWO"]
                
                df_day, valid_ticker = None, None
                for t in possible_targets:
                for t in possible_targets:
                    temp_day = yf.download(t, period="1y", interval="1d", progress=False)
                    if not temp_day.empty:
                        df_day = temp_day
                        valid_ticker = t
                        break
                
                if df_day is not None:
                    if isinstance(df_day.columns, pd.MultiIndex):
                        df_day.columns = df_day.columns.get_level_values(0)
                    if isinstance(df_day.columns, pd.MultiIndex):
                        df_day.columns = df_day.columns.get_level_values(0)
                    
                    # 進行金包銀檢測
                    # 進行金包銀檢測
                    df_60m = yf.download(valid_ticker, period="3mo", interval="60m", progress=False)
                    if isinstance(df_60m.columns, pd.MultiIndex):
                    if isinstance(df_60m.columns, pd.MultiIndex):
                        df_60m.columns = df_60m.columns.get_level_values(0)
                    
                    is_pattern = check_gold_silver_pattern(df_60m)
                    
                    st.success(f"成功找到資料: {valid_ticker}")
                    st.success(f"成功找到資料: {valid_ticker}")
                    col1, col2 = st.columns(2)
                    col1.metric("金包銀型態", "✅ 符合" if is_pattern else "❌ 未符合")
                    col2.metric("最新收盤價", f"{df_day['Close'].iloc[-1]:.2f}")
                    st.line_chart(df_day['Close'].tail(60))
                    col1.metric("金包銀型態", "✅ 符合" if is_pattern else "❌ 未符合")
                    col2.metric("最新收盤價", f"{df_day['Close'].iloc[-1]:.2f}")
                    st.line_chart(df_day['Close'].tail(60))
                else:
                    st.error(f"找不到 {ticker} 的資料，請確認代號是否正確。")
                    st.error(f"找不到 {ticker} 的資料，請確認代號是否正確。")

with tab2:
    st.subheader("全場掃描結果")
    
    # 【新增功能】：強制重新讀取按鈕
    if st.button("🔄 強制讀取最新數據"):
        st.rerun() # 按下後直接重跑程式，強制重新抓取檔案

    
    # 【新增功能】：強制重新讀取按鈕
    if st.button("🔄 強制讀取最新數據"):
        st.rerun() # 按下後直接重跑程式，強制重新抓取檔案

    file_path = 'results.csv'
    
    if os.path.exists(file_path):
        # 顯示最後更新時間
        # 顯示最後更新時間
        mtime = os.path.getmtime(file_path)
        last_updated = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        st.info(f"🕒 數據最後更新時間: {last_updated}")
        
        # 讀取 CSV
        # 讀取 CSV
        df = pd.read_csv(file_path)
        st.dataframe(df, use_container_width=True)
        
        # 下載按鈕
        # 下載按鈕
        st.download_button(
            label="📥 下載完整結果 (CSV)",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name='results.csv',
            mime='text/csv'
        )
    else:
        st.warning("尚未產生結果。若確認已執行過 scanner.py，代表目前市場上沒有股票符合您的金包銀嚴格條件。")