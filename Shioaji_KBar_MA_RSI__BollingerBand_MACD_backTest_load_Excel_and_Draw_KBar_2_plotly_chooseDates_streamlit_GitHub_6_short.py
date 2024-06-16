# 載入必要模組
import datetime
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# 主程式
def main():
    # 讀取數據
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
    KBar_dic['open'] = KBar_open_list
    KBar_time_list = list(KBar_dic['time'].values())
    KBar_time_list = [i.to_pydatetime() for i in KBar_time_list]
    KBar_dic['time'] = KBar_time_list
    KBar_low_list = list(KBar_dic['low'].values())
    KBar_dic['low'] = KBar_low_list
    KBar_high_list = list(KBar_dic['high'].values())
    KBar_dic['high'] = KBar_high_list
    KBar_close_list = list(KBar_dic['close'].values())
    KBar_dic['close'] = KBar_close_list
    KBar_volume_list = list(KBar_dic['volume'].values())
    KBar_dic['volume'] = KBar_volume_list

    # 設定K棒時間長度
    st.subheader("設定一根 K 棒的時間長度")
    timeframe = st.selectbox('選擇時間周期', ('日', '周', '月'))
    timeframe_mapping = {'日': 1440, '周': 10080, '月': 43200}
    cycle_duration = timeframe_mapping[timeframe]

    # 設定移動平均線的 K 棒長度
    st.subheader("設定計算移動平均MA的 K 棒數目")
    MAPeriod = st.selectbox('選擇一個整數', list(range(201)), index=10)

    KBar_df = pd.DataFrame(KBar_dic)
    KBar_df['MA'] = KBar_df['close'].rolling(window=MAPeriod).mean()

    # 繪製K線圖和移動平均線 MA
    with st.expander("K線圖, 移動平均線"):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Candlestick(x=KBar_df['time'], open=KBar_df['open'], high=KBar_df['high'],
                                     low=KBar_df['low'], close=KBar_df['close'], name='K線'), secondary_y=True)
        fig.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['volume'], name='成交量', marker=dict(color='black')),
                      secondary_y=False)
        fig.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA'], mode='lines', line=dict(color='orange', width=2),
                                 name=f'{MAPeriod}-根 K棒 移動平均線'), secondary_y=True)
        fig.layout.yaxis2.showgrid = True
        st.plotly_chart(fig, use_container_width=True)

    # 顯示資料表
    with st.expander("查看資料表"):
        st.dataframe(KBar_df)

# 執行主程式
if __name__ == "__main__":
    main()





















