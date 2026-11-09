
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하면 연도별 최고기온과 최저기온을 비교할 수 있어요!")

# CSV 파일 경로 확인
data_path = Path(__file__).parent / "temperature.csv"

# pages 폴더 안에 앱 파일이 있는 경우 상위 폴더도 확인
if not data_path.exists():
    data_path = Path(__file__).parent.parent / "temperature.csv"

# 데이터 불러오기
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="utf-8-sig")

    # 날짜 데이터 변환
    df["날짜"] = pd.to_datetime(
        df["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 기온 데이터 숫자로 변환
    df["최고기온(℃)"] = pd.to_numeric(
        df["최고기온(℃)"], errors="coerce"
    )

    df["최저기온(℃)"] = pd.to_numeric(
        df["최저기온(℃)"], errors="coerce"
    )

    # 연도와 월별로 중복 데이터 평균 계산
    df = df.groupby(
        ["연도", "월"],
        as_index=False
    )[["최고기온(℃)", "최저기온(℃)"]].mean()

    return df


# 데이터 불러오기 실행
try:
    df = load_data(str(data_path))

    if df.empty:
        st.error("분석할 데이터가 없습니다.")
        st.stop()

except FileNotFoundError:
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.info("CSV 파일을 app.py와 같은 폴더에 넣어주세요.")
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# 월 선택
month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

st.subheader("📅 분석할 월 선택")

selected_month = st.selectbox(
    "월을 선택하세요.",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x]
)

# 선택한 월의 데이터 추출
month_df = df[df["월"] == selected_month].copy()

# 연도순 정렬
month_df = month_df.sort_values("연도")

# 그래프 그리기
if not month_df.empty:

    fig = go.Figure()

    # 최고기온 그래프
    fig.add_trace(
        go.Scatter(
            x=month_df["연도"],
            y=month_df["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#F4A7C3",
                width=3
            ),
            marker=dict(size=7)
        )
    )

    # 최저기온 그래프
    fig.add_trace(
        go.Scatter(
            x=month_df["연도"],
            y=month_df["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#87CEEB",
                width=3
            ),
            marker=dict(size=7)
        )
    )

    # 그래프 레이아웃
    fig.update_layout(
        title={
            "text": "월별 기온분석",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis_title="연도",
        yaxis_title="온도 (℃)",
        legend_title="범례",
        hovermode="x unified",
        template="plotly_white",
        height=550
    )

    # 그래프 표시
    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # 데이터 표 표시
    st.subheader("📊 선택한 월의 기온 데이터")

    display_df = month_df.rename(
        columns={
            "연도": "연도",
            "최고기온(℃)": "최고기온 (℃)",
            "최저기온(℃)": "최저기온 (℃)"
        }
    )

    st.dataframe(
        display_df[
            ["연도", "최고기온 (℃)", "최저기온 (℃)"]
        ],
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("선택한 월의 데이터가 없습니다.")

# 데이터 출처 안내
st.caption("기온 데이터 분석 | Pandas와 Plotly 활용")
