# 載入必要模組
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import indicator_f_Lo2_short
import indicator_forKBar_short

# 設定網頁標題
st.set_page_config(page_title="金融資料視覺化呈現 (金融看板)", page_icon=":chart_with_upwards_trend:")

# 載入資料
@st.cache_data(ttl=3600, show_spinner="加載中...")  
def load_data(url):
    df = pd.read_pickle(url)
    return df

# 主程式
def main():
    # 載入資料
    df_original = load_data("kbars_2330_2022-01-01-2022-11-18.pkl")
    df_original = df_original.drop('Unnamed: 0', axis=1)

    # 設定日期範圍
    st.subheader("選擇開始與結束的日期")
    start_date = st.text_input('選擇開始日期 (格式: 2022-01-03)', '2022-01-03')
    end_date = st.text_input('選擇結束日期 (格式: 2022-11-18)', '2022-11-18')
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    df = df_original[(df_original['time'] >= start_date) & (df_original['time'] <= end_date)]

    # 轉換成字典格式
    KBar_dic = df.to_dict()
    KBar_open_list = list(KBar_dic['open'].values())
    KBar_dic['open'] = np.array(KBar_open_list)
    KBar_dic['product'] = np.repeat('tsmc', KBar_dic['open'].size)
    KBar_time_list = [i.to_pydatetime() for i in KBar_dic['time'].values()]
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

    # 設定K棒週期
    st.subheader("設定一根K棒的時間長度(分鐘)")
    cycle_duration = st.number_input('輸入一根K棒的時間長度(單位:分鐘, 一日=1440分鐘)', key="KBar_duration", value=1440)
    cycle_duration = int(cycle_duration)
    KBar = indicator_forKBar_short.KBar(start_date.strftime("%Y-%m-%d"), cycle_duration)

    # 繪製K線圖和移動平均線
    with st.expander("K線圖和移動平均線"):
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_trace(go.Candlestick(x=KBar_dic['time'],
                                      open=KBar_dic['open'], high=KBar_dic['high'],
                                      low=KBar_dic['low'], close=KBar_dic['close'], name='K線'),
                       secondary_y=True)
        fig1.add_trace(go.Scatter(x=KBar_dic['time'], y=pd.Series(KBar_dic['close']).rolling(window=10).mean(),
                                  mode='lines', name='10日移動平均線'), secondary_y=True)
        st.plotly_chart(fig1, use_container_width=True)

    # 繪製成交量圖
    with st.expander("成交量"):
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=KBar_dic['time'], y=KBar_dic['volume'], name='成交量', marker_color='blue'))
        st.plotly_chart(fig2, use_container_width=True)

    # 計算並繪製RSI指標
    with st.expander("RSI指標"):
        def calculate_rsi(df, period=14):
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        KBar_df = pd.DataFrame(KBar_dic)
        KBar_df['RSI'] = calculate_rsi(KBar_df)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['RSI'], mode='lines', name='RSI指標', marker_color='green'))
        st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main()













