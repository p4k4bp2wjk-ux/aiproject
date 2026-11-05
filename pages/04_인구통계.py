
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="부산광역시 인구 분석",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ 부산광역시 인구 통계 분석")
st.write("연령별 인구 변화와 연령대별 구·군 인구 순위를 분석해 보세요!")

# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

# 현재 py 파일은 pages 폴더
# CSV 파일은 상위 폴더에 있음

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "populattion.csv"

if not CSV_PATH.exists():
    st.error(
        "populattion.csv 파일을 찾을 수 없습니다. "
        "프로젝트 최상위 폴더에 파일이 있는지 확인해 주세요."
    )
    st.stop()

# 한글 인코딩 오류 방지
df = None

for encoding in ["cp949", "euc-kr", "utf-8-sig"]:
    try:
        df = pd.read_csv(
            CSV_PATH,
            encoding=encoding,
            dtype=str
        )
        break
    except UnicodeDecodeError:
        continue

if df is None:
    st.error("CSV 파일의 한글 인코딩을 읽을 수 없습니다.")
    st.stop()

# ==========================================
# 3. 인구 데이터를 숫자로 변환
# ==========================================

for col in df.columns[1:]:
    df[col] = pd.to_numeric(
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False),
        errors="coerce"
    )

# ==========================================
# 4. 행정구역 이름 정리
# ==========================================

df["행정구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)", "", regex=True)
    .str.strip()
)

# ==========================================
# 5. 성별 및 연령대 설정
# ==========================================

gender_options = {
    "전체": "거주자",
    "남성": "남_거주자",
    "여성": "여_거주자"
}

age_groups = [
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
]

years = [2025, 2024, 2023, 2022, 2021, 2020]

# ==========================================
# 6. 분석 조건 선택
# ==========================================

st.divider()
st.header("🔍 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:
    districts = df["행정구역명"].tolist()

    selected_district = st.selectbox(
        "📍 행정구역 선택",
        districts,
        key="district"
    )

with col2:
    selected_gender = st.selectbox(
        "👥 성별 선택",
        ["전체", "남성", "여성"],
        key="gender"
    )

with col3:
    selected_year = st.selectbox(
        "📅 연도 선택",
        years,
        key="year"
    )

gender_prefix = gender_options[selected_gender]
prefix = f"{selected_year}년_{gender_prefix}_"

# ==========================================
# 7. 첫 번째 기능
# 연령별 인구 꺾은선 그래프
# ==========================================

st.divider()
st.header("📈 연령별 인구 변화")

st.subheader(
    f"{selected_district} | {selected_year}년 | {selected_gender}"
)

# 선택한 행정구역의 데이터 찾기

selected_row = df[
    df["행정구역명"] == selected_district
]

if selected_row.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_row = selected_row.iloc[0]

# 연령별 데이터 추출

age_data = []

for age in age_groups:

    column = prefix + age

    if column in df.columns:

        population = selected_row[column]

        if pd.isna(population):
            population = 0

        age_data.append({
            "연령대": age,
            "나이": age_groups.index(age) * 10,
            "인구수": int(population)
        })

age_df = pd.DataFrame(age_data)

if age_df.empty:
    st.error("연령별 데이터를 찾을 수 없습니다.")
    st.stop()

# 전체 연령 인구 합계

total_population = age_df["인구수"].sum()

st.metric(
    label="연령별 인구 합계",
    value=f"{total_population:,}명"
)

# 꺾은선 그래프

fig1 = go.Figure()

fig1.add_trace(
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
            "%{customdata}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        ),
        customdata=age_df["연령대"]
    )
)

fig1.update_layout(
    height=550,
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial, sans-serif",
        size=13,
        color="#333333"
    ),
    xaxis=dict(
        title="나이",
        tickmode="array",
        tickvals=age_df["나이"],
        ticktext=age_df["연령대"],
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
    showlegend=False,
    margin=dict(
        l=70,
        r=30,
        t=30,
        b=90
    )
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ==========================================
# 8. 두 번째 기능
# 연령대별 인구가 가장 많은 행정구 순위
# ==========================================

st.divider()
st.header("🏆 연령대별 인구가 많은 행정구 순위")

st.write(
    "원하는 연령대를 선택하면 해당 연령 인구가 많은 "
    "부산의 구·군 순위를 확인할 수 있어요."
)

# 연령대 선택

selected_age = st.selectbox(
    "🎂 비교할 연령대 선택",
    age_groups,
    key="ranking_age"
)

# 부산광역시 전체 행은 제외하고 구·군만 비교

district_df = df[
    df["행정구역명"] != "부산광역시"
].copy()

# 선택한 연령대의 열 이름

ranking_column = prefix + selected_age

if ranking_column not in district_df.columns:

    st.error("선택한 연령대의 데이터를 찾을 수 없습니다.")

else:

    # 구·군별 인구수 추출

    ranking_df = district_df[
        ["행정구역명", ranking_column]
    ].copy()

    ranking_df = ranking_df.rename(
        columns={
            "행정구역명": "행정구역",
            ranking_column: "인구수"
        }
    )

    ranking_df["인구수"] = (
        ranking_df["인구수"].fillna(0).astype(int)
    )

    # 인구가 많은 순서대로 정렬

    ranking_df = ranking_df.sort_values(
        by="인구수",
        ascending=False
    ).reset_index(drop=True)

    # 순위 추가

    ranking_df.insert(
        0,
        "순위",
        range(1, len(ranking_df) + 1)
    )

    # 1위 지역 표시

    first_district = ranking_df.iloc[0]["행정구역"]
    first_population = ranking_df.iloc[0]["인구수"]

    st.success(
        f"🥇 {selected_age} 인구가 가장 많은 지역은 "
        f"{first_district}입니다! "
        f"({first_population:,}명)"
    )

    # 가로 막대그래프

    fig2 = go.Figure()

    fig2.add_trace(
        go.Bar(
            x=ranking_df["인구수"],
            y=ranking_df["행정구역"],
            orientation="h",
            marker=dict(
                color="#87CEEB"
            ),
            text=ranking_df["인구수"].apply(
                lambda x: f"{x:,}명"
            ),
            textposition="outside",
            hovertemplate=(
                "%{y}<br>"
                "인구수: %{x:,.0f}명"
                "<extra></extra>"
            )
        )
    )

    fig2.update_layout(
        height=650,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial, sans-serif",
            size=13,
            color="#333333"
        ),
        title=dict(
            text=f"{selected_year}년 {selected_gender} "
                 f"{selected_age} 인구 순위",
            x=0.5
        ),
        xaxis=dict(
            title="인구수 (명)",
            tickformat=",",
            showgrid=True,
            gridcolor="#DCEEF7",
            dtick=10000,
            rangemode="tozero"
        ),
        yaxis=dict(
            title="행정구역",
            categoryorder="total ascending"
        ),
        showlegend=False,
        margin=dict(
            l=100,
            r=100,
            t=70,
            b=60
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # 순위 데이터 표

    with st.expander("📋 구·군별 인구 순위 자세히 보기"):

        display_ranking = ranking_df.copy()

        display_ranking["인구수"] = (
            display_ranking["인구수"].apply(
                lambda x: f"{x:,}명"
            )
        )

        st.dataframe(
            display_ranking,
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# 9. 데이터 안내
# ==========================================

st.divider()

st.caption(
    "자료: 부산광역시 인구 통계 CSV | "
    "분석 기준: 연도별·성별·연령별 거주자 인구"
)

st.caption(
    "※ 연령대별 순위는 부산광역시 전체를 제외한 "
    "16개 구·군을 대상으로 계산합니다."
)
