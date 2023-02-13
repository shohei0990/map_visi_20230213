import streamlit as st                      # streamlit
from streamlit_folium import st_folium    # streamlitでfoliumを使う
import folium                               # folium
import pandas as pd                         # CSVをデータフレームとして読み込む
import requests
import json
from urllib.parse import urlencode
from geopy.distance import geodesic

# ページ設定
st.set_page_config(
    page_title="streamlit-foliumテスト",
    page_icon="🗾",
    layout="wide"
)

# 表示するデータを読み込み
df = pd.read_csv('map_info.csv')
select_columns_num = ['緯度', '経度']

# 地図の中心の緯度/経度、タイル、初期のズームサイズを指定します。
m = folium.Map(
    # 地図の中心位置の指定
    location=[df['緯度'][1], df['経度'][1]],
    # タイル、アトリビュートの指定
    tiles='https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png',
    attr='都道府県庁所在地、人口、面積(2016年)',
    # ズームを指定
    zoom_start=15
)


pre_df = df[select_columns_num]

for column in pre_df:
    pre_df[column] = pd.to_numeric(pre_df[column], errors='coerce')
df[select_columns_num] = pre_df


# --------------------------------------------------------------------------------------------------------------------
# パラメータリスト
api_key = 'Your API ID'
lat, lng = df['緯度'][1], df['経度'][1]
radius = 500
keyword = "コンビニ"
language = 'ja'

# エンドポイントURL
places_endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
# パラメータ
params = {
    "key": api_key,
    "location": f"{lat},{lng}",
    "radius": radius,
    "keyword": keyword,
    "language": language,
}

# URLエンコード
params_encoded = urlencode(params)
# リクエストURL生成
places_url = f"{places_endpoint}?{params_encoded}"

# 結果取得
r = requests.get(places_url)
data = r.json()
# 結果出力
print(json.dumps(data, indent=2))

# APIレスポンスを取得
places = r.json()["results"]

df_cb = pd.DataFrame(columns=['名称', '住所', '緯度', '経度'])

# 各コンビニの位置情報を表示
for place in places:
    temp = pd.DataFrame(data=[[place["name"], place["vicinity"], round(place["geometry"]["location"]["lat"], 6), round(
        place["geometry"]["location"]["lng"], 6)]], columns=df_cb.columns)
    df_cb = pd.concat([df_cb, temp])
    print("名称:", place["name"])
    print("住所:", place["vicinity"])
    print("緯度:", place["geometry"]["location"]["lat"])
    print("経度:", place["geometry"]["location"]["lng"])
    print("------------------------------")

df_cb = df_cb.reset_index()
home = (lat, lng)
home_d = (df["緯度"][1], df["経度"][1])

# 関数化


def Map_distance(x):
    home_dis = (x["緯度"], x["経度"])
    dis = geodesic(home, home_dis)
    return dis


df_cb['距離'] = df_cb.apply(Map_distance, axis=1)

for i, row in df_cb.iterrows():
    # ポップアップの作成(都道府県名＋都道府県庁所在地＋人口＋面積)
    pop = f"・名称…{row['名称']} <br>・距離[m]…{row['距離']}"
    folium.Marker(
        # 緯度と経度を指定
        location=[row['緯度'], row['経度']],
        # ツールチップの指定(都道府県名)
        tooltip=row['名称'],
        # ポップアップの指定
        popup=folium.Popup(pop, max_width=300),
        # アイコンの指定(アイコン、色)
        icon=folium.Icon(icon="bell", icon_color="white", color="blue")
    ).add_to(m)

# -------------------------------------------------------------------------------

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
