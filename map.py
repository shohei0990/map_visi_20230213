import streamlit as st                      # streamlit
from streamlit_folium import st_folium    # streamlitでfoliumを使う
import folium                               # folium
import pandas as pd                         # CSVをデータフレームとして読み込む

# ページ設定
st.set_page_config(
    page_title="streamlit-foliumテスト",
    page_icon="🗾",
    layout="wide"
)

# 地図の中心の緯度/経度、タイル、初期のズームサイズを指定します。
m = folium.Map(
    # 地図の中心位置の指定(今回は栃木県の県庁所在地を指定)
    location=[35.623516, 139.706985],
    # タイル、アトリビュートの指定
    tiles='https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png',
    attr='都道府県庁所在地、人口、面積(2016年)',
    # ズームを指定
    zoom_start=15
)

# 表示するデータを読み込み
df = pd.read_csv('map_info.csv')
select_columns_num = ['緯度', '経度']
pre_df = df[select_columns_num]

for column in pre_df:
    pre_df[column] = pd.to_numeric(pre_df[column], errors='coerce')
df[select_columns_num] = pre_df

# 読み込んだデータ(緯度・経度、ポップアップ用文字、アイコンを表示)
for i, row in df.iterrows():
    # ポップアップの作成(都道府県名＋都道府県庁所在地＋人口＋面積)
    pop = f"{row['カテゴリー']} <br>・家賃…{row['家賃']} <br>・面積…{row['面積']}<br>・築数…{row['築年数']}<br>・階数…{row['階数']}"
    folium.Marker(
        # 緯度と経度を指定
        location=[row['緯度'], row['経度']],
        # ツールチップの指定(都道府県名)
        tooltip=row['名称'],
        # ポップアップの指定
        popup=folium.Popup(pop, max_width=300),
        # アイコンの指定(アイコン、色)
        icon=folium.Icon(icon="home", icon_color="white", color="red")
    ).add_to(m)

st_data = st_folium(m, width=1200, height=800)
