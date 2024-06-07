# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 22:57:37 2024

@author: a0208
"""
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
import talib

# Streamlit應用程序佈局
st.title('金融看板交易程式')

# 下拉式選擇時間單位
time_unit = st.selectbox('選擇時間單位', ['日', '周', '月', '年'])

# 下拉式選擇股票
selected_stock = st.selectbox('選擇股票', ['台積電', '長榮'])

# 獲取所選股票的代碼
if selected_stock == '台積電':
    stock_code = '2330.TW'  # 台積電股票代碼
elif selected_stock == '長榮':
    stock_code = '2603.TW'  # 長榮股票代碼

# 下載股票數據
stock_data = yf.download(stock_code, period='5y')

# 根據所選的時間單位來重新抽樣數據
if time_unit == '日':
    resampled_data = stock_data
elif time_unit == '周':
    resampled_data = stock_data.resample('W').mean()
elif time_unit == '月':
    resampled_data = stock_data.resample('M').mean()
elif time_unit == '年':
    resampled_data = stock_data.resample('Y').mean()

# 計算移動平均線
resampled_data['MA10'] = talib.SMA(resampled_data['Close'], timeperiod=10)
resampled_data['MA30'] = talib.SMA(resampled_data['Close'], timeperiod=30)

# 計算相對強弱指標（RSI）
resampled_data['RSI'] = talib.RSI(resampled_data['Close'])

# 繪製K線圖
st.header('K線圖')
fig_candlestick = go.Figure(data=[go.Candlestick(x=resampled_data.index,
                                open=resampled_data['Open'],
                                high=resampled_data['High'],
                                low=resampled_data['Low'],
                                close=resampled_data['Close'])])
st.plotly_chart(fig_candlestick)

# 繪製技術性指標圖
st.header('技術性指標')
fig_indicator = go.Figure()

# 移動平均線
fig_indicator.add_trace(go.Scatter(x=resampled_data.index, y=resampled_data['MA10'], mode='lines', name='MA10'))
fig_indicator.add_trace(go.Scatter(x=resampled_data.index, y=resampled_data['MA30'], mode='lines', name='MA30'))

# RSI指標
fig_indicator.add_trace(go.Scatter(x=resampled_data.index, y=resampled_data['RSI'], mode='lines', name='RSI'))

st.plotly_chart(fig_indicator)


