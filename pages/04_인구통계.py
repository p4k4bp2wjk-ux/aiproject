
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# --------------------------------
# 1. 페이지 기본 설정
# --------------------------------
st.set_page_config(
    page_title="부산광역시 인구 분석",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ 부산광역시 연령별 인구 분석")
st.write("행정구역, 성별, 연도를 선택하여 연령별 인구를 확인해 보세요!")

# --------------------------------
# 2. CSV 파일 불러오기
# --------------------------------

# 현재 py 파일은 pages 폴더,
# CSV 파일은 그 상위 폴더에 있는 경우
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "populattion.csv"

# 파일이 없으면 현재 폴더에서도 검색
if not CSV_PATH.exists():
    CSV_PATH = Path("populattion.csv")

try:
    df = pd.read_csv(
        CSV_PATH,
        encoding="cp949",
        dtype=str
    )

except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "populattion.csv 파일이 프로젝트 상위 폴더에 있는지 확인해 주세요."
    )
    st.stop()

except UnicodeDecodeError:
    st.error(
        "CSV 파일의 인코딩을 확인해 주세요. "
        "현재 코드는 CP949 인코딩을 사용합니다."
    )
    st.stop()

# --------------------------------
# 3. 인구 데이터 숫자로 변환
# --------------------------------

for col in df.columns[1:]:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

# --------------------------------
# 4. 행정구역 이름 정리
# --------------------------------

# 예: 부산광역시 중구 (2611000000)
#     -> 부산광역시 중구

df["행정구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)", "", regex=True)
    .str.strip()
)

districts = df["행정구역명"].tolist()

# --------------------------------
# 5. 선택 메뉴 만들기
# --------------------------------

st.subheader("🔍 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:
    selected_district = st.selectbox(
        "📍 행정구역 선택",
        districts
    )

with col2:
    selected_gender = st.selectbox(
        "👥 성별 선택",
        ["전체", "남성", "여성"]
    )

with col3:
    selected_year = st.selectbox(
        "📅 연도 선택",
        [2025, 2024, 2023, 2022, 2021, 2020]
    )

# --------------------------------
# 6. 선택한 데이터 가져오기
# --------------------------------

# CSV 열 이름의 성별 표현과 연결
gender_name = {
    "전체": "거주자",
    "남성": "남",
    "여성": "여"
}

gender_prefix = gender_name[selected_gender]

# 선택한 행정구역 데이터 찾기
selected_row = df[
    df["행정구역명"] == selected_district
]

if selected_row.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_row = selected_row.iloc[0]

# --------------------------------
# 7. 연령별 인구 데이터 추출
# --------------------------------

prefix = f"{selected_year}년_{gender_prefix}_"

age_data = []

for column in df.columns:

    # 선택한 연도와 성별의 열만 추출
    if not column.startswith(prefix):
        continue

    # 총인구수와 연령구간인구수는 제외
    age_label = column[len(prefix):]

    if age_label in ["총인구수", "연령구간인구수"]:
        continue

    # 나이 숫자 추출
    match = re.search(r"(\d+)", age_label)

    if match is None:
        continue

    age = int(match.group(1))
    population = selected_row[column]

    if pd.isna(population):
        population = 0

    age_data.append({
        "나이": age,
        "연령": age_label,
        "인구수": int(population)
    })

# 나이순으로 정렬
age_df = pd.DataFrame(age_data)

if age_df.empty:
    st.error("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

age_df = age_df.sort_values("나이")

# --------------------------------
# 8. 선택한 조건 표시
# --------------------------------

st.divider()

st.subheader(
    f"📊 {selected_district} {selected_year}년 {selected_gender} 연령별 인구"
)

total_population = age_df["인구수"].sum()

st.metric(
    label="연령별 인구 합계",
    value=f"{total_population:,}명"
)

# --------------------------------
# 9. 꺾은선 그래프 만들기
# --------------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=age_df["나이"],
        y=age_df["인구수"],
        mode="lines+markers",
        name="인구수",
        line=dict(
            color="#87CEEB",
            width=3
        ),
        marker=dict(
            color="#87CEEB",
            size=9
        ),
        hovertemplate=(
            "%{x}세 이상 연령대<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)

# --------------------------------
# 10. 그래프 디자인
# --------------------------------

fig.update_layout(
    height=600,

    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Malgun Gothic, AppleGothic, NanumGothic, sans-serif",
        size=14,
        color="#333333"
    ),

    xaxis=dict(
        title="나이",
        tickmode="array",
        tickvals=list(range(0, 101, 10)),
        ticktext=[
            "0~9세",
            "10~19세",
            "20~29세",
            "30~39세",
            "40~49세",
            "50~59세",
            "60~69세",
            "70~79세",
            "80~89세",
            "90~99세",
            "100세 이상"
        ],
        range=[-3, 103],
        showgrid=True,
        gridcolor="#DCEEF7",
        gridwidth=1,
        zeroline=False
    ),

    yaxis=dict(
        title="인구수 (명)",
        tickformat=",",
        dtick=100000,
        rangemode="tozero",
        showgrid=True,
        gridcolor="#DCEEF7",
        gridwidth=1,
        zeroline=False
    ),

    margin=dict(
        l=70,
        r=30,
        t=40,
        b=90
    ),

    showlegend=False
)

# --------------------------------
# 11. 스트림릿에 그래프 출력
# --------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------
# 12. 데이터 표 출력
# --------------------------------

with st.expander("📋 연령별 인구 데이터 자세히 보기"):

    display_df = age_df.copy()

    display_df["인구수"] = display_df["인구수"].apply(
        lambda x: f"{x:,}명"
    )

    display_df = display_df.rename(
        columns={
            "나이": "나이 기준",
            "연령": "연령 구간",
            "인구수": "인구수"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "자료: 업로드된 부산광역시 인구 통계 CSV | "
    "연령별 인구수 기준"
)
