

import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🇰🇷",
    layout="wide"
)

st.title("🇰🇷 서울 외국인 인기 관광지 TOP 10")
st.write("외국인 관광객들이 즐겨 찾는 서울의 대표 관광지를 지도에서 만나보세요! 🗺️")

# 관광지 데이터
places = [
    {
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "쇼핑과 먹거리",
        "description": "다양한 화장품 가게와 패션 매장, 맛있는 길거리 음식이 가득한 서울의 대표 쇼핑 거리입니다."
    },
    {
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망과 야경",
        "description": "남산 정상에 위치한 서울의 랜드마크로 아름다운 서울 전경과 야경을 감상할 수 있습니다."
    },
    {
        "name": "코엑스",
        "english": "COEX",
        "lat": 37.5126,
        "lon": 127.0588,
        "category": "쇼핑과 문화",
        "description": "대형 쇼핑몰과 전시장이 있는 복합 문화 공간입니다. 별마당도서관도 유명합니다."
    },
    {
        "name": "강남역",
        "english": "Gangnam Station",
        "lat": 37.4979,
        "lon": 127.0276,
        "category": "쇼핑과 도시문화",
        "description": "세련된 카페와 맛집, 다양한 쇼핑 매장이 모여 있는 서울의 대표 번화가입니다."
    },
    {
        "name": "홍대 거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "예술과 공연",
        "description": "거리 공연과 음악, 개성 있는 상점들을 만날 수 있는 젊음과 예술의 거리입니다."
    },
    {
        "name": "동대문디자인플라자",
        "english": "DDP",
        "lat": 37.5669,
        "lon": 127.0095,
        "category": "건축과 디자인",
        "description": "독특한 곡선형 건축물로 유명하며 다양한 전시와 디자인 행사가 열립니다."
    },
    {
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사와 전통",
        "description": "조선 왕조의 대표 궁궐로 한국의 아름다운 전통 건축과 역사를 경험할 수 있습니다."
    },
    {
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통문화",
        "description": "전통 한옥이 모여 있는 아름다운 마을로 한국의 옛 주거 문화를 느낄 수 있습니다."
    },
    {
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "전통시장과 음식",
        "description": "빈대떡과 다양한 한국 음식을 맛볼 수 있는 서울의 유명한 전통시장입니다."
    },
    {
        "name": "남대문시장",
        "english": "Namdaemun Market",
        "lat": 37.5592,
        "lon": 126.9777,
        "category": "전통시장과 쇼핑",
        "description": "오랜 역사를 가진 전통시장으로 의류, 액세서리, 생활용품과 먹거리를 판매합니다."
    }
]

# 서울 지도 생성
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 지도에 관광지 마커 표시
for place in places:

    popup_text = f"""
    <h4>{place['name']}</h4>
    <b>{place['english']}</b><br>
    {place['description']}
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=place["name"],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background-color:#E74C3C;
                color:white;
                border-radius:50%;
                width:32px;
                height:32px;
                text-align:center;
                line-height:32px;
                font-weight:bold;
                border:2px solid white;
                box-shadow:0 2px 5px #888;
            ">
                {places.index(place) + 1}
            </div>
            """
        )
    ).add_to(m)

# 지도 화면 출력
st.subheader("📍 서울 관광지 지도")

st_folium(
    m,
    width=None,
    height=600,
    use_container_width=True
)

st.caption("지도 위의 숫자 마커를 클릭하면 관광지 정보를 볼 수 있습니다.")

# 관광지 설명
st.divider()
st.header("✨ 서울 관광지 TOP 10 소개")

for i in range(0, len(places), 2):
    col1, col2 = st.columns(2)

    for col, place in zip([col1, col2], places[i:i+2]):
        with col:
            with st.container(border=True):
                st.subheader(f"{places.index(place)+1}. {place['name']}")
                st.caption(
                    f"{place['english']} | {place['category']}"
                )
                st.write(place["description"])

                url = (
                    "https://www.google.com/maps/search/?api=1&query="
                    f"{place['lat']},{place['lon']}"
                )
                st.link_button("📍 구글 지도에서 보기", url)

st.divider()
st.success("서울의 아름다운 관광지를 즐겁게 여행해 보세요! 💙")
