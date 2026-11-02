
import streamlit as st
import folium
from streamlit_folium import st_folium

# =====================================
# 🇰🇷 서울 외국인 인기 관광지 TOP 10
# =====================================

st.title("🇰🇷 서울 외국인 인기 관광지 TOP 10")

st.markdown("""
서울을 방문하는 외국인 관광객들이 즐겨 찾는
대표 관광지 10곳을 지도에서 만나보세요! 🗺️

지도에 표시된 숫자를 클릭하면 관광지 정보를 확인할 수 있습니다.
""")

st.divider()

# =====================================
# 1. 관광지 데이터
# =====================================

places = [
    {
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "🛍️ 쇼핑과 먹거리",
        "description": "화장품 매장, 패션 상점, 길거리 음식이 가득한 서울의 대표 쇼핑 거리입니다.",
        "tip": "저녁에 방문하면 다양한 길거리 음식을 즐길 수 있어요."
    },
    {
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "🌃 전망과 야경",
        "description": "남산 정상에 위치한 서울의 랜드마크로 아름다운 서울 전경을 감상할 수 있습니다.",
        "tip": "해 질 무렵 방문하면 멋진 야경을 볼 수 있어요."
    },
    {
        "name": "코엑스",
        "english": "COEX",
        "lat": 37.5126,
        "lon": 127.0588,
        "category": "🏬 쇼핑과 문화",
        "description": "대형 쇼핑몰과 전시장이 있는 복합 문화 공간입니다. 별마당도서관도 유명합니다.",
        "tip": "별마당도서관에서 멋진 사진을 찍어 보세요."
    },
    {
        "name": "강남역",
        "english": "Gangnam Station",
        "lat": 37.4979,
        "lon": 127.0276,
        "category": "☕ 쇼핑과 도시문화",
        "description": "세련된 카페와 맛집, 다양한 쇼핑 매장이 모여 있는 서울의 대표 번화가입니다.",
        "tip": "골목 곳곳에 있는 개성 있는 카페도 둘러보세요."
    },
    {
        "name": "홍대 거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "🎸 예술과 공연",
        "description": "거리 공연과 음악, 개성 있는 상점들을 만날 수 있는 젊음과 예술의 거리입니다.",
        "tip": "주말에는 다양한 거리 공연을 구경해 보세요."
    },
    {
        "name": "동대문디자인플라자",
        "english": "DDP",
        "lat": 37.5669,
        "lon": 127.0095,
        "category": "🏛️ 건축과 디자인",
        "description": "독특한 곡선형 건축물로 유명하며 다양한 전시와 디자인 행사가 열립니다.",
        "tip": "밤에 조명이 켜진 건물 외관도 아름다워요."
    },
    {
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "👑 역사와 전통",
        "description": "조선 왕조의 대표 궁궐로 한국의 아름다운 전통 건축과 역사를 경험할 수 있습니다.",
        "tip": "한복을 입고 궁궐을 둘러보는 것도 추천해요."
    },
    {
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "🏡 전통문화",
        "description": "전통 한옥이 모여 있는 아름다운 마을로 한국의 옛 주거 문화를 느낄 수 있습니다.",
        "tip": "주민들이 생활하는 공간이므로 조용히 관람해 주세요."
    },
    {
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "🥘 전통시장과 음식",
        "description": "빈대떡과 다양한 한국 음식을 맛볼 수 있는 서울의 유명한 전통시장입니다.",
        "tip": "다양한 한국 길거리 음식을 경험해 보세요."
    },
    {
        "name": "남대문시장",
        "english": "Namdaemun Market",
        "lat": 37.5592,
        "lon": 126.9777,
        "category": "🛒 전통시장과 쇼핑",
        "description": "오랜 역사를 가진 전통시장으로 의류, 액세서리, 생활용품과 먹거리를 판매합니다.",
        "tip": "다양한 한국 기념품을 찾아보세요."
    }
]

# =====================================
# 2. 서울 지도 만들기
# =====================================

st.subheader("📍 서울 관광지 지도")

m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 관광지 마커 추가
for i, place in enumerate(places, start=1):

    popup_html = f"""
    <div style="width:230px; font-family:sans-serif;">
        <h3>{i}. {place['name']}</h3>
        <b>{place['english']}</b>
        <hr>
        <p>{place['category']}</p>
        <p>{place['description']}</p>
        <p>💡 {place['tip']}</p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{i}. {place['name']}",
        popup=folium.Popup(popup_html, max_width=280),
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
                font-size:15px;
                border:2px solid white;
                box-shadow:0 2px 5px #888;
            ">
                {i}
            </div>
            """,
            icon_size=(32, 32),
            icon_anchor=(16, 16)
        )
    ).add_to(m)

# 지도 범위 설정
coordinates = [
    [place["lat"], place["lon"]]
    for place in places
]

m.fit_bounds(coordinates, padding=(25, 25))

# 지도 출력
st_folium(
    m,
    use_container_width=True,
    height=600,
    returned_objects=[]
)

st.caption("🔴 지도 위의 숫자를 클릭하면 관광지 상세 정보를 확인할 수 있습니다.")

st.divider()

# =====================================
# 3. 관광지 상세 설명
# =====================================

st.header("✨ 서울 인기 관광지 TOP 10 소개")

st.write("각 관광지의 특징과 여행 팁을 확인해 보세요!")

for i in range(0, len(places), 2):

    col1, col2 = st.columns(2)

    for col, place in zip(
        [col1, col2],
        places[i:i+2]
    ):

        with col:

            with st.container(border=True):

                rank = places.index(place) + 1

                st.subheader(
                    f"{rank}. {place['name']}"
                )

                st.caption(
                    f"{place['english']} | {place['category']}"
                )

                st.write(
                    place["description"]
                )

                st.info(
                    f"💡 여행 팁: {place['tip']}"
                )

                google_map_url = (
                    "https://www.google.com/maps/search/?api=1&query="
                    f"{place['lat']},{place['lon']}"
                )

                st.link_button(
                    "📍 구글 지도에서 위치 보기",
                    google_map_url
                )

# =====================================
# 4. 마무리
# =====================================

st.divider()

st.success(
    "🇰🇷 서울의 아름다운 관광지를 즐겁게 여행해 보세요!"
)

st.markdown("""
**🗺️ 지도 안내**

- 지도 서비스: OpenStreetMap
- 관광지 위치: 각 장소의 대표 좌표
- 관광지 순번: 추천 목록 번호이며 공식 통계 순위는 아닙니다.
""")

st.caption("서울 관광지 TOP 10 | Made with Streamlit 💙")

