
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

# =====================================
# 2. CSV 파일 경로 설정
# =====================================

# 현재 py 파일의 상위 폴더에 있는 CSV 파일
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "countriesMBTI_16types.csv"


# =====================================
# 3. 데이터 불러오기
# =====================================

@st.cache_data
def load_data(file_path):

    df = pd.read_csv(file_path)

    # 컬럼명 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    # 국가 컬럼 확인
    if "Country" not in df.columns:
        raise ValueError("Country 컬럼을 찾을 수 없습니다.")

    # 국가 이름 정리
    df = df.dropna(subset=["Country"]).copy()
    df["Country"] = df["Country"].astype(str).str.strip()

    # MBTI 컬럼 추출
    mbti_columns = [
        col for col in df.columns
        if col != "Country"
    ]

    # 숫자 데이터 변환
    for col in mbti_columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        ).fillna(0)

    return df, mbti_columns


# =====================================
# 4. 메인 화면
# =====================================

st.title("🌍 국가별 MBTI 비율 분석")
st.write(
    "세계 여러 나라의 MBTI 유형별 비율을 "
    "그래프로 확인해 보세요! 💙"
)

st.markdown("---")


# =====================================
# 5. CSV 파일 확인 및 불러오기
# =====================================

if not DATA_FILE.exists():

    st.error("CSV 파일을 찾을 수 없습니다!")

    st.write("현재 찾고 있는 경로:")
    st.code(str(DATA_FILE))

    st.info(
        "CSV 파일이 app.py와 같은 상위 폴더에 "
        "있는지 확인해 주세요."
    )

    st.stop()


try:

    df, mbti_columns = load_data(DATA_FILE)

except Exception as e:

    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.exception(e)
    st.stop()


# =====================================
# 6. 국가 선택
# =====================================

countries = sorted(df["Country"].unique().tolist())

if len(countries) == 0:
    st.error("선택할 국가 데이터가 없습니다.")
    st.stop()

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "🗺️ 분석할 국가를 선택하세요!",
    countries,
    index=default_index
)


# =====================================
# 7. 선택한 국가의 MBTI 데이터
# =====================================

country_data = df[
    df["Country"] == selected_country
].iloc[0]

chart_data = pd.DataFrame({

    "MBTI": mbti_columns,

    "비율": [
        float(country_data[col])
        for col in mbti_columns
    ]

})

# CSV 값이 소수 형태이므로 백분율로 변환
chart_data["비율"] = chart_data["비율"] * 100

# 비율이 높은 순서대로 정렬
chart_data = chart_data.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)


# =====================================
# 8. 그래프 색상 설정
# =====================================

colors = []

total = len(chart_data)

for i in range(total):

    # 1위는 진한 파란색
    if i == 0:

        colors.append("#2563EB")

    else:

        # 하늘색에서 점점 연해지는 그라데이션
        start = (135, 206, 235)
        end = (234, 247, 255)

        ratio = (i - 1) / max(total - 2, 1)

        rgb = tuple(
            round(
                start[j] +
                (end[j] - start[j]) * ratio
            )
            for j in range(3)
        )

        color = "#{:02X}{:02X}{:02X}".format(*rgb)

        colors.append(color)


# =====================================
# 9. 주요 통계 표시
# =====================================

top_mbti = chart_data.iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🌍 선택 국가",
        selected_country
    )

with col2:
    st.metric(
        "🏆 가장 높은 MBTI",
        top_mbti["MBTI"]
    )

with col3:
    st.metric(
        "📊 최고 비율",
        f'{top_mbti["비율"]:.2f}%'
    )


st.markdown("---")


# =====================================
# 10. MBTI 막대그래프
# =====================================

st.subheader(
    f"📊 {selected_country}의 MBTI 유형별 비율"
)

fig = px.bar(

    chart_data,

    x="비율",

    y="MBTI",

    orientation="h",

    text=chart_data["비율"].map(
        lambda x: f"{x:.2f}%"
    )

)

# 막대 색상 적용
fig.update_traces(

    marker_color=colors,

    textposition="outside",

    cliponaxis=False,

    hovertemplate=
    "<b>%{y}</b><br>" +
    "비율: %{x:.2f}%" +
    "<extra></extra>"

)


# =====================================
# 11. 그래프 디자인
# =====================================

fig.update_layout(

    yaxis=dict(

        categoryorder="array",

        categoryarray=(
            chart_data["MBTI"].tolist()[::-1]
        ),

        title=""

    ),

    xaxis=dict(

        title="MBTI 비율 (%)",

        rangemode="tozero"

    ),

    height=650,

    showlegend=False,

    margin=dict(
        l=30,
        r=80,
        t=30,
        b=50
    ),

    plot_bgcolor="white",

    paper_bgcolor="white",

    font=dict(
        family="Arial, sans-serif",
        size=13
    )

)


# =====================================
# 12. 스트림릿에 그래프 출력
# =====================================

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 13. MBTI 순위표
# =====================================

with st.expander("🏆 MBTI 비율 순위표 확인하기"):

    ranking = chart_data[
        ["MBTI", "비율"]
    ].copy()

    ranking.index = range(
        1,
        len(ranking) + 1
    )

    ranking.index.name = "순위"

    ranking["비율"] = ranking["비율"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )


# =====================================
# 14. 마무리 안내
# =====================================

st.success(
    "💙 다른 국가를 선택하면 그래프가 자동으로 바뀝니다!"
)

st.caption(
    "※ 본 자료는 국가별 MBTI 통계 데이터의 시각화이며, "
    "개인의 성격을 판단하는 기준은 아닙니다."
)
