
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------
# 1. 기본 설정
# --------------------------------

st.title("🌡️ 서울 기온 데이터 분석")
st.write("서울의 기온 변화를 다양한 그래프로 확인해 보세요!")

# CSV 파일은 상위 폴더에 있음
BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / "temperature.csv"

# 월 이름
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}


# --------------------------------
# 2. 데이터 불러오기
# --------------------------------

@st.cache_data
def load_data(file_path):

    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 월 이름과 연도 추출
    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    # 일시에서 연도 추출
    year_text = df["일시"].astype(str).str.extract(
        r"-(\d{2})$"
    )[0]

    # 07은 2007, 26은 2026으로 변환
    df["연도"] = pd.to_numeric(
        year_text, errors="coerce"
    ) + 2000

    # 월 추출
    month_text = df["일시"].astype(str).str[:3]
    df["월"] = month_text.map(month_dict)

    # 숫자형으로 변환
    temp_columns = [
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in temp_columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    # 2007~2026년 데이터만 사용
    df = df[
        (df["연도"] >= 2007) &
        (df["연도"] <= 2026)
    ].copy()

    return df


# 파일 확인
if not CSV_PATH.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.write("파일 경로:", str(CSV_PATH))
    st.stop()

# 데이터 읽기
try:
    df = load_data(str(CSV_PATH))
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# --------------------------------
# 3. 기능 1
# 서울 월별 평균기온 그래프
# --------------------------------

st.divider()

st.header("📊 1. 서울 월별 평균기온")

st.write(
    "2007년부터 2026년까지의 데이터를 이용해 "
    "각 월의 평균기온을 비교합니다."
)

# 월별 평균기온 계산
monthly_avg = (
    df.groupby("월")["평균기온(℃)"]
    .mean()
    .reindex(range(1, 13))
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=[month_names[m] for m in monthly_avg.index],
        y=monthly_avg.values,
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(
            color="#F4A7C3",
            width=3
        ),
        marker=dict(size=9)
    )
)

fig1.update_layout(
    title="서울 월별 평균기온",
    xaxis_title="월",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    height=450
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# --------------------------------
# 4. 기능 2
# 연도별 최고기온과 최저기온
# --------------------------------

st.divider()

st.header("📈 2. 연도별 최고기온과 최저기온")

st.write(
    "각 연도에 기록된 최고기온의 최댓값과 "
    "최저기온의 최솟값을 비교합니다."
)

# 연도별 최고기온과 최저기온 계산
year_temp = (
    df.groupby("연도")
    .agg({
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .reset_index()
)

year_temp = year_temp.sort_values("연도")

fig2 = go.Figure()

# 최고기온
fig2.add_trace(
    go.Scatter(
        x=year_temp["연도"],
        y=year_temp["최고기온(℃)"],
        mode="lines+markers",
        name="연도별 최고기온",
        line=dict(
            color="#F4A7C3",
            width=3
        ),
        marker=dict(size=8)
    )
)

# 최저기온
fig2.add_trace(
    go.Scatter(
        x=year_temp["연도"],
        y=year_temp["최저기온(℃)"],
        mode="lines+markers",
        name="연도별 최저기온",
        line=dict(
            color="#87CEEB",
            width=3
        ),
        marker=dict(size=8)
    )
)

fig2.update_layout(
    title="연도별 최고기온과 최저기온",
    xaxis_title="연도",
    yaxis_title="온도 (℃)",
    legend_title="범례",
    hovermode="x unified",
    template="plotly_white",
    height=500,
    xaxis=dict(
        tickmode="linear",
        dtick=1
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# 연도별 데이터 표
with st.expander("연도별 기온 데이터 보기"):
    st.dataframe(
        year_temp.rename(
            columns={
                "최고기온(℃)": "최고기온 (℃)",
                "최저기온(℃)": "최저기온 (℃)"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------
# 5. 기능 3
# 두 연도 비교 그래프
# --------------------------------

st.divider()

st.header("🔍 3. 두 연도 기온 비교")

st.write(
    "원하는 두 연도를 선택하면 "
    "월별 평균기온을 비교할 수 있습니다."
)

# 데이터에 존재하는 연도만 선택
years = sorted(
    df["연도"].dropna().unique().astype(int).tolist()
)

if len(years) >= 2:

    col1, col2 = st.columns(2)

    with col1:
        year1 = st.selectbox(
            "첫 번째 연도 선택",
            years,
            index=max(0, len(years)-2)
        )

    with col2:
        year2 = st.selectbox(
            "두 번째 연도 선택",
            years,
            index=len(years)-1
        )

    if year1 == year2:
        st.warning("서로 다른 연도 2개를 선택해 주세요.")

    else:

        # 선택한 두 연도 데이터 추출
        compare_df = df[
            df["연도"].isin([year1, year2])
        ]

        # 연도별 월평균기온 계산
        compare_avg = (
            compare_df.groupby(
                ["연도", "월"]
            )["평균기온(℃)"]
            .mean()
            .reset_index()
        )

        fig3 = go.Figure()

        colors = ["#F4A7C3", "#87CEEB"]

        for i, year in enumerate([year1, year2]):

            temp_data = compare_avg[
                compare_avg["연도"] == year
            ].sort_values("월")

            fig3.add_trace(
                go.Scatter(
                    x=[
                        month_names[int(m)]
                        for m in temp_data["월"]
                    ],
                    y=temp_data["평균기온(℃)"],
                    mode="lines+markers",
                    name=f"{year}년",
                    line=dict(
                        color=colors[i],
                        width=3
                    ),
                    marker=dict(size=9)
                )
            )

        fig3.update_layout(
            title=f"{year1}년과 {year2}년 월별 평균기온 비교",
            xaxis_title="월",
            yaxis_title="평균기온 (℃)",
            legend_title="연도",
            hovermode="x unified",
            template="plotly_white",
            height=500
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        # 비교 데이터 표
        st.subheader("📋 두 연도 비교 데이터")

        compare_table = compare_avg.pivot(
            index="월",
            columns="연도",
            values="평균기온(℃)"
        )

        compare_table.index = [
            month_names[int(m)]
            for m in compare_table.index
        ]

        st.dataframe(
            compare_table,
            use_container_width=True
        )

else:
    st.warning("비교할 연도 데이터가 부족합니다.")


# --------------------------------
# 6. 마무리
# --------------------------------

st.divider()

st.caption(
    "🌡️ 서울 기온 데이터 분석 | "
    "Pandas + Plotly + Streamlit"
)

