
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

# 데이터 파일 경로
DATA_FILE = Path(__file__).parent / "countriesMBTI_16types.csv"


# CSV 데이터 불러오기
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    data.columns = data.columns.astype(str).str.strip()

    if "Country" not in data.columns:
        raise ValueError("Country 컬럼이 없습니다.")

    data = data.dropna(subset=["Country"]).copy()
    data["Country"] = data["Country"].astype(str).str.strip()

    mbti_columns = [
        col for col in data.columns
        if col != "Country"
    ]

    for col in mbti_columns:
        data[col] = pd.to_numeric(
            data[col], errors="coerce"
        ).fillna(0)

    return data, mbti_columns


# 제목
st.title("🌍 국가별 MBTI 비율 분석")
st.write(
    "국가를 선택하면 해당 국가의 "
    "16가지 MBTI 유형별 비율을 확인할 수 있어요!"
)

st.caption(
    "158개 국가의 MBTI 데이터를 활용한 분석 서비스입니다."
)

# 데이터 불러오기
try:

    if not DATA_FILE.exists():
        st.error(
            "CSV 파일을 찾을 수 없습니다. "
            "app.py와 같은 폴더에 CSV 파일을 넣어주세요."
        )
        st.stop()

    df, mbti_columns = load_data(DATA_FILE)

    if not mbti_columns:
        st.error("MBTI 유형 데이터를 찾을 수 없습니다.")
        st.stop()

    # 국가 선택
    countries = sorted(df["Country"].unique())

    default_index = (
        countries.index("South Korea")
        if "South Korea" in countries
        else 0
    )

    selected_country = st.selectbox(
        "🗺️ 국가를 선택하세요!",
        countries,
        index=default_index
    )

    # 선택한 국가 데이터
    country_data = df[
        df["Country"] == selected_country
    ].iloc[0]

    # 그래프 데이터 생성
    chart_data = pd.DataFrame({
        "MBTI": mbti_columns,
        "비율": [
            float(country_data[col])
            for col in mbti_columns
        ]
    })

    # 비율을 퍼센트로 변환
    if chart_data["비율"].max() <= 1:
        chart_data["비율"] *= 100

    chart_data = chart_data.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    # 그래프 색상 설정
    colors = []

    total = len(chart_data)

    for i in range(total):

        # 1위는 진한 파란색
        if i == 0:
            colors.append("#2563EB")

        else:
            # 나머지는 하늘색에서 점점 연해지는 색상
            start = (135, 206, 235)
            end = (234, 247, 255)

            denominator = max(total - 2, 1)
            ratio = (i - 1) / denominator

            rgb = tuple(
                round(
                    start[j] +
                    (end[j] - start[j]) * ratio
                )
                for j in range(3)
            )

            colors.append(
                "#{:02X}{:02X}{:02X}".format(*rgb)
            )

    # 가장 높은 MBTI
    top_mbti = chart_data.iloc[0]

    # 핵심 정보
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🌍 선택 국가",
        selected_country
    )

    col2.metric(
        "🏆 가장 높은 MBTI",
        top_mbti["MBTI"]
    )

    col3.metric(
        "📊 최고 비율",
        f'{top_mbti["비율"]:.2f}%'
    )

    # 그래프 제목
    st.subheader(
        f"📊 {selected_country}의 MBTI 유형별 비율"
    )

    # 막대 그래프
    fig = px.bar(
        chart_data,
        x="비율",
        y="MBTI",
        orientation="h",
        text=chart_data["비율"].map(
            lambda x: f"{x:.2f}%"
        )
    )

    fig.update_traces(
        marker_color=colors,
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )
    )

    # 그래프 디자인
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
            r=70,
            t=25,
            b=45
        ),

        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            family="Arial, sans-serif",
            size=13
        )
    )

    # 화면에 그래프 출력
    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # 순위표
    with st.expander("🏆 MBTI 비율 순위표 보기"):

        ranking = chart_data[
            ["MBTI", "비율"]
        ].copy()

        ranking.index = range(
            1,
            len(ranking) + 1
        )

        ranking.index.name = "순위"

        ranking["비율"] = ranking[
            "비율"
        ].map(lambda x: f"{x:.2f}%")

        st.dataframe(
            ranking,
            use_container_width=True
        )

    st.success(
        "💙 다른 국가를 선택하면 그래프가 자동으로 바뀝니다!"
    )

    st.caption(
        "※ 국가별 통계는 참고용 자료이며 "
        "개인의 성격을 판단하는 기준이 아닙니다."
    )

except Exception as e:

    st.error(
        "데이터를 처리하는 중 문제가 발생했어요."
    )

    st.exception(e)
