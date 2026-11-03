
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="세계 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)


# =====================================
# 2. CSV 파일 경로
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "countriesMBTI_16types.csv"


# =====================================
# 3. 데이터 불러오기
# =====================================

@st.cache_data
def load_data(file_path):

    df = pd.read_csv(file_path)

    df.columns = df.columns.astype(str).str.strip()

    if "Country" not in df.columns:
        raise ValueError("Country 컬럼이 없습니다.")

    df = df.dropna(subset=["Country"]).copy()

    df["Country"] = df["Country"].astype(str).str.strip()

    mbti_columns = [
        col for col in df.columns
        if col != "Country"
    ]

    for col in mbti_columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        ).fillna(0)

    # 원본 데이터가 소수 형태이면 퍼센트로 변환
    if df[mbti_columns].max().max() <= 1:
        df[mbti_columns] = df[mbti_columns] * 100

    return df, mbti_columns


# =====================================
# 4. 제목
# =====================================

st.title("🌍 WORLD MBTI ANALYSIS")

st.subheader("세계 국가별 MBTI 유형 분석 📊")

st.write(
    "국가를 선택하거나 MBTI를 선택해서 "
    "세계의 MBTI 분포를 알아보세요! 💙"
)

st.markdown("---")


# =====================================
# 5. 데이터 확인
# =====================================

if not DATA_FILE.exists():

    st.error("CSV 파일을 찾을 수 없습니다!")

    st.code(str(DATA_FILE))

    st.stop()


try:

    df, mbti_columns = load_data(DATA_FILE)

except Exception as e:

    st.error("데이터를 불러오는 중 오류가 발생했습니다.")

    st.exception(e)

    st.stop()


if len(mbti_columns) == 0 or len(df) == 0:
    st.error("분석할 데이터가 없습니다.")
    st.stop()


# =====================================
# 6. 분석 메뉴
# =====================================

tab1, tab2 = st.tabs([
    "🌎 국가별 MBTI 비율",
    "🏆 MBTI별 국가 순위"
])


# =====================================
# TAB 1. 국가별 MBTI 비율
# =====================================

with tab1:

    st.header("🌎 국가별 MBTI 분석")

    countries = sorted(df["Country"].unique())

    default_index = (
        countries.index("South Korea")
        if "South Korea" in countries
        else 0
    )

    selected_country = st.selectbox(
        "🗺️ 국가를 선택하세요!",
        countries,
        index=default_index,
        key="country_select"
    )

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

    chart_data = chart_data.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    # 색상 설정
    colors = []

    total = len(chart_data)

    for i in range(total):

        if i == 0:
            colors.append("#2563EB")

        else:

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

            colors.append(
                "#{:02X}{:02X}{:02X}".format(*rgb)
            )

    top = chart_data.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("🌍 선택 국가", selected_country)
    col2.metric("🏆 1위 MBTI", top["MBTI"])
    col3.metric("📊 최고 비율", f'{top["비율"]:.2f}%')

    fig1 = px.bar(
        chart_data,
        x="비율",
        y="MBTI",
        orientation="h",
        text=chart_data["비율"].map(
            lambda x: f"{x:.2f}%"
        )
    )

    fig1.update_traces(
        marker_color=colors,
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )
    )

    fig1.update_layout(
        yaxis=dict(
            categoryorder="array",
            categoryarray=chart_data["MBTI"].tolist()[::-1],
            title=""
        ),
        xaxis=dict(
            title="비율 (%)",
            rangemode="tozero"
        ),
        height=650,
        showlegend=False,
        margin=dict(l=30, r=80, t=30, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )


# =====================================
# TAB 2. MBTI별 국가 순위
# =====================================

with tab2:

    st.header("🏆 MBTI별 국가 순위")

    st.write(
        "MBTI 유형을 선택하면 해당 유형의 비율이 "
        "높은 국가부터 순서대로 보여줘요!"
    )

    st.markdown("---")

    # MBTI 선택
    selected_mbti = st.selectbox(
        "💙 분석할 MBTI 유형을 선택하세요!",
        mbti_columns,
        key="mbti_select"
    )

    # 선택한 MBTI의 국가별 비율
    ranking_data = df[
        ["Country", selected_mbti]
    ].copy()

    ranking_data = ranking_data.rename(
        columns={
            selected_mbti: "비율"
        }
    )

    # 높은 비율부터 정렬
    ranking_data = ranking_data.sort_values(
        by="비율",
        ascending=False
    ).reset_index(drop=True)

    # 순위 추가
    ranking_data.index = range(
        1,
        len(ranking_data) + 1
    )

    ranking_data.index.name = "순위"

    # 1위 국가
    first_country = ranking_data.iloc[0]

    # 통계 표시
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💙 선택 MBTI",
        selected_mbti
    )

    col2.metric(
        "🥇 1위 국가",
        first_country["Country"]
    )

    col3.metric(
        "📊 1위 비율",
        f'{first_country["비율"]:.2f}%'
    )

    st.markdown("---")

    # 표시할 국가 수 선택
    display_count = st.selectbox(
        "📌 그래프에 표시할 국가 수",
        [10, 20, 30, 50, 100, len(ranking_data)],
        index=1,
        key="display_count"
    )

    # 선택한 수만큼 표시
    chart_ranking = ranking_data.head(
        display_count
    ).reset_index()

    # 국가별 색상 설정
    colors = []

    total = len(chart_ranking)

    for i in range(total):

        # 1위는 진한 파란색
        if i == 0:

            colors.append("#2563EB")

        else:

            # 하늘색에서 점점 흐려지는 그라데이션
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

            colors.append(
                "#{:02X}{:02X}{:02X}".format(*rgb)
            )

    # 그래프 제목
    st.subheader(
        f"🌍 {selected_mbti} 비율이 높은 국가 TOP {display_count}"
    )

    # 가로 막대그래프
    fig2 = px.bar(
        chart_ranking,
        x="비율",
        y="Country",
        orientation="h",
        text=chart_ranking["비율"].map(
            lambda x: f"{x:.2f}%"
        ),
        hover_data=["순위"]
    )

    fig2.update_traces(
        marker_color=colors,
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )
    )

    # 1위 국가를 맨 위에 배치
    fig2.update_layout(

        yaxis=dict(
            categoryorder="array",
            categoryarray=(
                chart_ranking["Country"].tolist()[::-1]
            ),
            title=""
        ),

        xaxis=dict(
            title=f"{selected_mbti} 비율 (%)",
            rangemode="tozero"
        ),

        height=max(500, display_count * 30),

        showlegend=False,

        margin=dict(
            l=30,
            r=80,
            t=30,
            b=45
        ),

        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            family="Arial, sans-serif",
            size=12
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # 국가 순위표
    with st.expander("🏆 전체 국가 순위표 확인하기"):

        table_data = ranking_data.copy()

        table_data["비율"] = table_data[
            "비율"
        ].map(lambda x: f"{x:.2f}%")

        st.dataframe(
            table_data,
            use_container_width=True
        )

    st.success(
        f"💙 {selected_mbti} 유형의 국가별 순위 분석 완료!"
    )


# =====================================
# 7. 하단 안내
# =====================================

st.markdown("---")

st.caption(
    "🌍 WORLD MBTI ANALYSIS | 국가별 MBTI 데이터 시각화"
)

st.caption(
    "※ 통계 데이터는 참고용이며 개인의 성격이나 "
    "특성을 확정적으로 나타내지 않습니다."
)
