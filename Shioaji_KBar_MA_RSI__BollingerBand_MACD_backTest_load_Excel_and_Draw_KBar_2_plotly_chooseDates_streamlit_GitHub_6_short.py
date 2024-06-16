# 載入必要模組
import os
import numpy as np
import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as stc
import indicator_forKBar_short

# 設定頁面樣式
html_temp = """
        <div style="background-color:#3872fb;padding:10px;border-radius:10px">
        <h1 style="color:white;text-align:center;">金融資料視覺化呈現 (金融看板) </h1>
        <h2 style="color:white;text-align:center;">Financial Dashboard </h2>
        </div>
        """
stc.html(html_temp)

# 讀取Pickle文件
@st.cache_data(ttl=3600, show_spinner="正在加載資料...")
def load_data(url):
    df = pd.read_pickle(url)
    return df

df_original = load_data("kbars_2330_2022-01-01-2022-11-18.pkl")
df_original = df_original.drop('Unnamed: 0', axis=1)

# 選擇資料區間
st.subheader("選擇開始與結束的日期, 區間:2022-01-03 至 2022-11-18")
start_date = st.text_input('選擇開始日期 (日期格式: 2022-01-03)', '2022-01-03')
end_date = st.text_input('選擇結束日期 (日期格式: 2022-11-18)', '2022-11-18')
start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
df = df_original[(df_original['time'] >= start_date) & (df_original['time'] <= end_date)]

# 轉化為字典
KBar_dic = df.to_dict()
KBar_open_list = list(KBar_dic['open'].values())
KBar_dic['open'] = np.array(KBar_open_list)
KBar_dic['product'] = np.repeat('tsmc', KBar_dic['open'].size)
KBar_time_list = list(KBar_dic['time'].values())
KBar_time_list = [i.to_pydatetime() for i in KBar_time_list]
KBar_dic['time'] = np.array(KBar_time_list)
KBar_low_list = list(KBar_dic['low'].values())
KBar_dic['low'] = np.array(KBar_low_list)
KBar_high_list = list(KBar_dic['high'].values())
KBar_dic['high'] = np.array(KBar_high_list)
KBar_close_list = list(KBar_dic['close'].values())
KBar_dic['close'] = np.array(KBar_close_list)
KBar_volume_list = list(KBar_dic['volume'].values())
KBar_dic['volume'] = np.array(KBar_volume_list)
KBar_amount_list = list(KBar_dic['amount'].values())
KBar_dic['amount'] = np.array(KBar_amount_list)

# 設定K棒時間長度
st.subheader("設定一根 K 棒的時間長度")
timeframe = st.selectbox('選擇時間周期', ('日', '周', '月'))
timeframe_mapping = {'日': 1440, '周': 10080, '月': 43200}
cycle_duration = timeframe_mapping[timeframe]

Date = start_date.strftime("%Y-%m-%d")
KBar = indicator_forKBar_short.KBar(Date, cycle_duration)

for i in range(KBar_dic['time'].size):
    time = KBar_dic['time'][i]
    open_price = KBar_dic['open'][i]
    close_price = KBar_dic['close'][i]
    low_price = KBar_dic['low'][i]
    high_price = KBar_dic['high'][i]
    qty = KBar_dic['volume'][i]
    amount = KBar_dic['amount'][i]
    tag = KBar.AddPrice(time, open_price, close_price, low_price, high_price, qty)

KBar_dic = {}
KBar_dic['time'] = KBar.TAKBar['time']
KBar_dic['product'] = np.repeat('tsmc', KBar_dic['time'].size)
KBar_dic['open'] = KBar.TAKBar['open']
KBar_dic['high'] = KBar.TAKBar['high']
KBar_dic['low'] = KBar.TAKBar['low']
KBar_dic['close'] = KBar.TAKBar['close']
KBar_dic['volume'] = KBar.TAKBar['volume']

# 計算各種技術指標
KBar_df = pd.DataFrame(KBar_dic)

# 設定長短移動平均線的 K棒 長度
st.subheader("設定計算長移動平均線(MA)的 K 棒數目")
LongMAPeriod = st.selectbox('選擇一個整數', list(range(201)), index=10)
st.subheader("設定計算短移動平均線(MA)的 K 棒數目")
ShortMAPeriod = st.selectbox('選擇一個整數', list(range(201)), index=2)

KBar_df['MA_long'] = KBar_df['close'].rolling(window=LongMAPeriod).mean()
KBar_df['MA_short'] = KBar_df['close'].rolling(window=ShortMAPeriod).mean()

last_nan_index_MA = KBar_df['MA_long'][::-1].index[KBar_df['MA_long'][::-1].apply(pd.isna)][0]

# RSI策略
st.subheader("設定計算長RSI的 K 棒數目")
LongRSIPeriod = st.selectbox('選擇一個整數', list(range(201)), index=10, key='LongRSI')
st.subheader("設定計算短RSI的 K 棒數目")
ShortRSIPeriod = st.selectbox('選擇一個整數', list(range(201)), index=2, key='ShortRSI')

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

KBar_df['RSI_long'] = calculate_rsi(KBar_df, LongRSIPeriod)
KBar_df['RSI_short'] = calculate_rsi(KBar_df, ShortRSIPeriod)
KBar_df['RSI_Middle'] = np.array([50] * len(KBar_dic['time']))

last_nan_index_RSI = KBar_df['RSI_long'][::-1].index[KBar_df['RSI_long'][::-1].apply(pd.isna)][0]

KBar_df.columns = [i[0].upper() + i[1:] for i in KBar_df.columns]

st.subheader("畫圖")
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# K線圖, 移動平均線 MA
with st.expander("K線圖, 移動平均線"):
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Candlestick(x=KBar_df['Time'], open=KBar_df['Open'], high=KBar_df['High'],
                                  low=KBar_df['Low'], close=KBar_df['Close'], name='K線'), secondary_y=True)
    fig1.add_trace(go.Bar(x=KBar_df['Time'], y=KBar_df['Volume'], name='成交量', marker=dict(color='black')),
                   secondary_y=False)
    fig1.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_MA + 1:], y=KBar_df['MA_long'][last_nan_index_MA + 1:],
                              mode='lines', line=dict(color='orange', width=2), name=f'{LongMAPeriod}-根 K棒 移動平均線'),
                   secondary_y=True)
    fig1.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_MA + 1:], y=KBar_df['MA_short'][last_nan_index_MA + 1:],
                              mode='lines', line=dict(color='pink', width=2), name=f'{ShortMAPeriod}-根 K棒 移動平均線'),
                   secondary_y=True)
    fig1.layout.yaxis2.showgrid = True
    st.plotly_chart(fig1, use_container_width=True)

# K線圖, RSI
with st.expander("K線圖, 長短 RSI"):
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(go.Candlestick(x=KBar_df['Time'], open=KBar_df['Open'], high=KBar_df['High'],
                                  low=KBar_df['Low'], close=KBar_df['Close'], name='K線'), secondary_y=True)
    fig2.add_trace(go.Bar(x=KBar_df['Time'], y=KBar_df['Volume'], name='成交量', marker=dict(color='black')),
                   secondary_y=False)
    fig2.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_RSI + 1:], y=KBar_df['RSI_long'][last_nan_index_RSI + 1:],
                              mode='lines', line=dict(color='orange', width=2), name=f'{LongRSIPeriod}-根 K棒 RSI'),
                   secondary_y=True)
    fig2.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_RSI + 1:], y=KBar_df['RSI_short'][last_nan_index_RSI + 1:],
                              mode='lines', line=dict(color='pink', width=2), name=f'{ShortRSIPeriod}-根 K棒 RSI'),
                   secondary_y=True)
    fig2.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_RSI + 1:], y=KBar_df['RSI_Middle'][last_nan_index_RSI + 1:],
                              mode='lines', line=dict(color='blue', width=1), name='中線 50'),
                   secondary_y=True)
    fig2.layout.yaxis2.showgrid = True
    st.plotly_chart(fig2, use_container_width=True)

with st.expander("查看資料表"):
    st.dataframe(KBar_df)

# 預設時間區間 2022-01-03 到 2022-11-18
# 起始日期 '2022-01-03'
# 結束日期 '2022-11-18'






















