
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# ----------------------------------
# 1. 페이지 설정
# ----------------------------------
st.set_page_config(
    page_title="서울 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 예측")
st.write("과거 기온 데이터를 이용해 선형회귀 알고리즘으로 미래 기온을 예측해 보세요!")

# ----------------------------------
# 2. CSV 파일 경로 설정
# ----------------------------------
# 현재 py 파일의 상위 폴더 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# CSV 파일은 pages 폴더의 상위 폴더에 있음
CSV_PATH = BASE_DIR / "temperature(1).csv"

if not CSV_PATH.exists():
    st.error(f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}")
    st.stop()

# ----------------------------------
# 3. CSV 데이터 불러오기
# ----------------------------------
try:
    df = pd.read_csv(CSV_PATH, encoding="cp949")
except UnicodeDecodeError:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

# 필요한 열 확인
required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일의 열 이름을 확인해 주세요. "
        "필요한 열: 일시, 평균기온(℃)"
    )
    st.stop()

# ----------------------------------
# 4. 데이터 전처리
# ----------------------------------
# 날짜 형식 변환
df["일시"] = pd.to_datetime(
    df["일시"],
    errors="coerce"
)

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=["연도", "월", "평균기온(℃)"]
).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

df = df.sort_values("연도")

if df.empty:
    st.error("분석할 수 있는 기온 데이터가 없습니다.")
    st.stop()

# ----------------------------------
# 5. 사용자 입력
# ----------------------------------
st.subheader("🔍 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측하고 싶은 월",
        range(1, 13),
        format_func=lambda x: f"{x}월"
    )

with col2:
    latest_year = int(df["연도"].max())

    selected_year = st.number_input(
        "예측하고 싶은 연도",
        min_value=latest_year + 1,
        max_value=latest_year + 100,
        value=latest_year + 5,
        step=1
    )

selected_year = int(selected_year)

# ----------------------------------
# 6. 선택한 월의 데이터 추출
# ----------------------------------
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("선형회귀 분석에 필요한 데이터가 부족합니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

# ----------------------------------
# 7. 선형회귀 모델 학습
# ----------------------------------
model = LinearRegression()

model.fit(X, y)

# 미래 기온 예측
prediction = model.predict(
    pd.DataFrame({"연도": [selected_year]})
)[0]

# 회귀식 정보
slope = model.coef_[0]
intercept = model.intercept_
r2 = model.score(X, y)

# ----------------------------------
# 8. 예측 결과 표시
# ----------------------------------
st.divider()

st.subheader(
    f"📌 {selected_year}년 {selected_month}월 예측 결과"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "🌡️ 예측 평균기온",
    f"{prediction:.1f}℃"
)

col2.metric(
    "📊 분석 데이터 개수",
    f"{len(month_df)}개"
)

col3.metric(
    "📈 결정계수 R²",
    f"{r2:.3f}"
)

st.info(
    f"{selected_year}년 {selected_month}월의 "
    f"예측 평균기온은 {prediction:.1f}℃입니다."
)

# ----------------------------------
# 9. 그래프 생성
# ----------------------------------
st.subheader("📈 과거 기온과 미래 예측 그래프")

line_years = list(
    range(
        int(month_df["연도"].min()),
        selected_year + 1
    )
)

line_df = pd.DataFrame({
    "연도": line_years
})

line_predictions = model.predict(line_df)

fig = go.Figure()

# 실제 관측 데이터
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#2471A3",
            size=9
        ),
        hovertemplate="%{x}년<br>실제 기온: %{y:.2f}℃<extra></extra>"
    )
)

# 선형회귀 직선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_predictions,
        mode="lines",
        name="선형회귀 추세선",
        line=dict(
            color="#E67E22",
            width=3
        ),
        hovertemplate="%{x}년<br>회귀선: %{y:.2f}℃<extra></extra>"
    )
)

# 실제값과 예측값 사이의 오차
residual_x = []
residual_y = []

for _, row in month_df.iterrows():

    year = int(row["연도"])
    actual = row["평균기온(℃)"]

    fitted = model.predict(
        pd.DataFrame({"연도": [year]})
    )[0]

    residual_x.extend([year, year, None])
    residual_y.extend([actual, fitted, None])

fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="실제값과 회귀선의 오차",
        line=dict(
            color="gray",
            width=1,
            dash="dot"
        ),
        hoverinfo="skip"
    )
)

# 미래 예측 지점
fig.add_trace(
    go.Scatter(
        x=[selected_year],
        y=[prediction],
        mode="markers+text",
        name="미래 예측 기온",
        marker=dict(
            color="#E74C3C",
            size=17,
            symbol="star"
        ),
        text=[f"{prediction:.1f}℃"],
        textposition="top center",
        textfont=dict(size=14)
    )
)

fig.update_layout(
    title=f"{selected_month}월 연도별 평균기온 분석",
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    template="plotly_white",
    height=600,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        y=1.12
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------
# 10. 선형회귀 방정식
# ----------------------------------
st.subheader("🧮 선형회귀 분석 결과")

sign = "+" if intercept >= 0 else "-"

st.code(
    f"평균기온 = {slope:.4f} × 연도 {sign} {abs(intercept):.2f}"
)

st.write(f"기울기: {slope:.4f}")
st.write(f"절편: {intercept:.2f}")
st.write(f"결정계수(R²): {r2:.4f}")

if slope > 0:
    st.success(
        f"과거 데이터에서 {selected_month}월 평균기온은 "
        f"연평균 약 {slope:.3f}℃ 상승하는 경향을 보입니다."
    )
elif slope < 0:
    st.info(
        f"과거 데이터에서 {selected_month}월 평균기온은 "
        f"연평균 약 {abs(slope):.3f}℃ 하락하는 경향을 보입니다."
    )
else:
    st.info("과거 데이터에서 뚜렷한 상승 또는 하락 경향이 없습니다.")

# ----------------------------------
# 11. 과거 기온 데이터 표
# ----------------------------------
with st.expander("📋 과거 기온 데이터 확인하기"):

    st.dataframe(
        month_df[["연도", "평균기온(℃)"]],
        use_container_width=True,
        hide_index=True
    )

# ----------------------------------
# 12. 선형회귀 알고리즘 설명
# ----------------------------------
st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.write("""
선형회귀는 여러 데이터 사이의 관계를 분석하여
가장 적합한 직선을 찾고, 그 직선을 이용해
새로운 값을 예측하는 머신러닝 알고리즘입니다.
""")

st.markdown("### ① 실제 데이터 수집")

st.write("""
선택한 월의 과거 연도별 평균기온을 수집합니다.
예를 들어 1월을 선택하면 모든 연도의 1월 평균기온을
분석 데이터로 사용합니다.
""")

st.markdown("### ② 가장 적합한 직선 찾기")

st.write("""
파란색 점은 실제 관측된 평균기온이고,
주황색 직선은 선형회귀 알고리즘이 찾은 추세선입니다.

선형회귀는 실제 기온과 직선이 예측한 기온 사이의
오차를 계산합니다. 그리고 오차의 제곱을 모두 더한
값이 가장 작아지도록 직선을 결정합니다.
""")

st.markdown("### ③ 미래 기온 예측하기")

st.write(f"""
찾아낸 직선의 기울기와 절편을 이용해
{selected_year}년 {selected_month}월의 평균기온을 예측합니다.

그래프의 빨간색 별 모양 점이 미래 예측 기온입니다.
""")

st.markdown("### ④ 그래프 색깔 이해하기")

st.write("""
🔵 파란 점: 실제 관측된 평균기온

🟠 주황색 선: 선형회귀가 계산한 추세선

🔴 빨간 별: 미래 예측 평균기온

회색 점선: 실제 기온과 회귀선 사이의 오차
""")

st.markdown("### ⑤ 선형회귀의 장점과 한계")

st.write("""
선형회귀는 데이터의 전체적인 상승 또는 하락 경향을
쉽게 파악할 수 있다는 장점이 있습니다.

하지만 기온은 지구온난화, 기후변화, 자연적인 변동 등
다양한 요인의 영향을 받습니다.

따라서 과거의 직선적인 경향이 미래에도 똑같이
이어진다고 보장할 수 없습니다.

특히 먼 미래를 예측할수록 오차가 커질 수 있으므로
예측값은 실제 기온이 아닌 통계적인 추정값으로
이해해야 합니다.
""")

st.caption(
    "※ 본 분석은 과거 월별 평균기온만을 이용한 "
    "단순 선형회귀 결과입니다."
)
