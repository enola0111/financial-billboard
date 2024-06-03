# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 21:03:39 2024

@author: a0208
"""
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import talib

# 設定網頁標題
st.title('股票資訊與交易策略分析')

# 創建下拉式選單以選擇股票
stock_choice = st.selectbox('選擇股票', ['台積電', '長榮'])

# 選擇時間範圍
start_date = st.date_input('開始日期', pd.to_datetime('2019-12-31'))
end_date = st.date_input('結束日期', pd.to_datetime('2024-01-01'))

# 使用yfinance套件獲取股票資料
if stock_choice == '台積電':
    stock_symbol = '2330.TW'
elif stock_choice == '長榮':
    stock_symbol = '2603.TW'

stock_data = yf.download(stock_symbol, start=start_date, end=end_date)

# 繪製k線圖
st.subheader('K線圖')
plt.figure(figsize=(10, 5))
plt.plot(stock_data['Close'], label='Close Price', color='blue')
plt.title('Close Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='upper left')
st.pyplot(plt)

# 計算常見技術指標
st.subheader('技術指標')

# 移動平均線
stock_data['SMA'] = talib.SMA(stock_data['Close'], timeperiod=20)
plt.figure(figsize=(10, 5))
plt.plot(stock_data['Close'], label='Close Price', color='blue')
plt.plot(stock_data['SMA'], label='20-Day SMA', color='red')
plt.title('20-Day SMA')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='upper left')
st.pyplot(plt)

# MACD
macd, signal, _ = talib.MACD(stock_data['Close'])
stock_data['MACD'] = macd
stock_data['Signal'] = signal
plt.figure(figsize=(10, 5))
plt.plot(macd, label='MACD', color='blue')
plt.plot(signal, label='Signal', color='red')
plt.title('MACD')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend(loc='upper left')
st.pyplot(plt)

# RSI
rsi = talib.RSI(stock_data['Close'])
plt.figure(figsize=(10, 5))
plt.plot(rsi, label='RSI', color='blue')
plt.title('RSI')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend(loc='upper left')
st.pyplot(plt)




