
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

# --------------------------------------
# 1. 페이지 설정
# --------------------------------------
st.set_page_config(
    page_title="서울 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 예측")
st.write(
    "3가지 머신러닝 회귀 알고리즘을 이용하여 "
    "미래의 기온을 예측하고 결과를 비교해 보세요!"
)

# --------------------------------------
# 2. CSV 파일 경로
# --------------------------------------
# py 파일은 pages 폴더 안에 있음
# CSV 파일은 pages 폴더의 상위 폴더에 있음

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "temperature.csv"

if not CSV_PATH.exists():
    st.error(f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}")
    st.stop()

# --------------------------------------
# 3. CSV 데이터 불러오기
# --------------------------------------
try:
    df = pd.read_csv(CSV_PATH, encoding="cp949")
except UnicodeDecodeError:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

# 필요한 열 확인
required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

# --------------------------------------
# 4. 데이터 전처리
# --------------------------------------
df["일시"] = pd.to_datetime(
    df["일시"],
    format="%b-%y",
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

# 연도와 월별 평균기온 정리
df = (
    df.groupby(["연도", "월"], as_index=False)
    ["평균기온(℃)"].mean()
)

df = df.sort_values("연도")

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

latest_year = int(df["연도"].max())

# --------------------------------------
# 5. 사용자 입력
# --------------------------------------
st.divider()
st.subheader("🔍 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요.",
        range(1, 13),
        format_func=lambda x: f"{x}월"
    )

with col2:
    selected_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=latest_year + 1,
        max_value=latest_year + 100,
        value=latest_year + 5,
        step=1
    )

selected_year = int(selected_year)

# --------------------------------------
# 6. 회귀 알고리즘 선택
# --------------------------------------
st.subheader("🤖 회귀 알고리즘 선택")

algorithm_names = [
    "선형회귀 (Linear Regression)",
    "의사결정나무 회귀 (Decision Tree)",
    "랜덤포레스트 회귀 (Random Forest)"
]

selected_algorithm = st.selectbox(
    "사용할 알고리즘을 선택하세요.",
    algorithm_names
)

# 알고리즘 설명
if selected_algorithm == algorithm_names[0]:
    st.info(
        "📈 선형회귀: 과거 기온 데이터의 전체적인 "
        "상승 및 하락 추세를 직선으로 학습합니다."
    )

elif selected_algorithm == algorithm_names[1]:
    st.info(
        "🌳 의사결정나무: 데이터를 여러 구간으로 나누고 "
        "각 구간의 평균적인 기온을 학습합니다."
    )

else:
    st.info(
        "🌲 랜덤포레스트: 여러 개의 의사결정나무를 학습하고 "
        "각 나무의 예측 결과를 평균 내어 기온을 예측합니다."
    )

# --------------------------------------
# 7. 선택한 월의 데이터 추출
# --------------------------------------
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 3:
    st.error("회귀 분석을 위한 데이터가 부족합니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

# --------------------------------------
# 8. 세 가지 회귀 모델 생성
# --------------------------------------
models = {
    algorithm_names[0]: LinearRegression(),

    algorithm_names[1]: DecisionTreeRegressor(
        max_depth=3,
        random_state=42
    ),

    algorithm_names[2]: RandomForestRegressor(
        n_estimators=300,
        max_depth=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
}

# 모든 모델 학습
for name, model in models.items():
    model.fit(X, y)

# --------------------------------------
# 9. 세 가지 알고리즘 예측
# --------------------------------------
future_X = pd.DataFrame({
    "연도": [selected_year]
})

predictions = {}

for name, model in models.items():

    pred = model.predict(future_X)[0]

    predictions[name] = float(pred)

# 선택한 알고리즘의 예측값
selected_prediction = predictions[selected_algorithm]

# --------------------------------------
# 10. 예측 결과 표시
# --------------------------------------
st.divider()

st.subheader(
    f"📌 {selected_year}년 {selected_month}월 예측 결과"
)

st.metric(
    "🌡️ 선택한 알고리즘의 예측 평균기온",
    f"{selected_prediction:.2f}℃"
)

st.success(
    f"{selected_algorithm} 알고리즘의 예측 결과는 "
    f"{selected_prediction:.2f}℃입니다."
)

# --------------------------------------
# 11. 세 가지 알고리즘 결과 비교
# --------------------------------------
st.subheader("📊 알고리즘별 예측 결과 비교")

comparison_data = []

for name, prediction in predictions.items():

    comparison_data.append({
        "알고리즘": name,
        "예측 평균기온(℃)": round(prediction, 2),
        "선택 여부": "⭐ 선택됨" if name == selected_algorithm else ""
    })

comparison_df = pd.DataFrame(comparison_data)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------
# 12. 그래프 생성
# --------------------------------------
st.divider()

st.subheader("📈 세 가지 회귀 알고리즘 그래프 비교")

min_year = int(month_df["연도"].min())

line_years = list(
    range(min_year, selected_year + 1)
)

line_X = pd.DataFrame({
    "연도": line_years
})

fig = go.Figure()

# 실제 관측 기온
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#2471A3",
            size=9
        )
    )
)

# 알고리즘별 그래프 색상
colors = {
    algorithm_names[0]: "#E67E22",
    algorithm_names[1]: "#16A085",
    algorithm_names[2]: "#8E44AD"
}

# 알고리즘별 추세선과 미래 예측점
for name, model in models.items():

    line_predictions = model.predict(line_X)

    is_selected = name == selected_algorithm

    # 알고리즘별 예측선
    fig.add_trace(
        go.Scatter(
            x=line_years,
            y=line_predictions,
            mode="lines",
            name=name,
            line=dict(
                color=colors[name],
                width=4 if is_selected else 2,
                dash="solid" if is_selected else "dash"
            )
        )
    )

    # 미래 예측점
    fig.add_trace(
        go.Scatter(
            x=[selected_year],
            y=[predictions[name]],
            mode="markers+text",
            name=f"{name} 예측값",
            marker=dict(
                color=colors[name],
                size=14 if is_selected else 10,
                symbol="star" if is_selected else "circle"
            ),
            text=[
                f"{predictions[name]:.1f}℃"
                if is_selected else ""
            ],
            textposition="top center",
            showlegend=False
        )
    )

fig.update_layout(
    title=f"{selected_month}월 연도별 평균기온 및 알고리즘 비교",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    height=650,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        y=1.12
    )
)

fig.update_xaxes(
    dtick=max(
        1,
        (selected_year - min_year) // 10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    "파란 점은 실제 관측값이며, 나머지 세 가지 선은 "
    "각 회귀 알고리즘의 예측 결과입니다. "
    "선택한 알고리즘은 굵은 실선으로 표시됩니다."
)

# --------------------------------------
# 13. 알고리즘별 특징 설명
# --------------------------------------
st.divider()

st.subheader("📚 회귀 알고리즘 3가지 비교")

with st.expander("① 선형회귀 (Linear Regression)"):
    st.write("""
    선형회귀는 데이터의 관계를 가장 잘 설명하는
    직선을 찾는 알고리즘입니다.

    실제 기온과 직선이 예측한 기온 사이의
    오차 제곱합이 최소가 되도록 직선을 계산합니다.

    장점:
    - 원리를 이해하기 쉽습니다.
    - 전체적인 기온 상승과 하락 추세를 확인하기 좋습니다.

    단점:
    - 기온 변화가 직선 형태가 아닐 경우
      정확도가 떨어질 수 있습니다.
    """)

with st.expander("② 의사결정나무 회귀 (Decision Tree)"):
    st.write("""
    의사결정나무 회귀는 데이터를 여러 구간으로 나누고
    각 구간의 평균적인 값을 이용하여 예측합니다.

    장점:
    - 직선이 아닌 복잡한 관계도 학습할 수 있습니다.
    - 데이터가 어떤 구간으로 나뉘는지 이해하기 쉽습니다.

    단점:
    - 학습 데이터에 지나치게 맞춰질 수 있습니다.
    - 과거 데이터의 범위를 벗어난 미래 예측에는
      한계가 있습니다.
    """)

with st.expander("③ 랜덤포레스트 회귀 (Random Forest)"):
    st.write("""
    랜덤포레스트는 여러 개의 의사결정나무를 만들고
    각 나무의 예측값을 평균 내는 앙상블 알고리즘입니다.

    장점:
    - 여러 나무의 결과를 종합합니다.
    - 개별 의사결정나무의 불안정성을 줄일 수 있습니다.
    - 다양한 데이터 관계를 학습할 수 있습니다.

    단점:
    - 선형회귀보다 원리를 이해하기 복잡합니다.
    - 미래 연도처럼 학습 범위를 벗어난 값의 예측에는
      한계가 있습니다.
    """)

# --------------------------------------
# 14. 결과 해석
# --------------------------------------
st.subheader("🔎 알고리즘별 예측 차이 분석")

max_name = max(predictions, key=predictions.get)
min_name = min(predictions, key=predictions.get)

difference = (
    predictions[max_name] - predictions[min_name]
)

st.write(
    f"가장 높은 기온을 예측한 알고리즘은 "
    f"**{max_name}**입니다."
)

st.write(
    f"가장 낮은 기온을 예측한 알고리즘은 "
    f"**{min_name}**입니다."
)

st.write(
    f"세 알고리즘의 예측 기온 차이는 "
    f"**{difference:.2f}℃**입니다."
)

if difference < 0.01:
    st.info(
        "세 알고리즘의 예측 결과가 거의 같습니다."
    )
else:
    st.info(
        "같은 과거 기온 데이터를 사용해도 "
        "알고리즘의 학습 방식에 따라 "
        "미래 예측 결과가 달라질 수 있습니다."
    )

st.warning(
    "주의: 의사결정나무와 랜덤포레스트는 학습 데이터의 "
    "연도 범위를 벗어나면 과거 마지막 구간의 예측값이 "
    "유지될 수 있습니다. 따라서 세 모델의 미래 예측값은 "
    "실제 미래 기온을 보장하지 않는 통계적 추정치입니다."
)

# --------------------------------------
# 15. 과거 기온 데이터 확인
# --------------------------------------
with st.expander("📋 과거 기온 데이터 확인하기"):

    st.dataframe(
        month_df[["연도", "평균기온(℃)"]],
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "서울 월별 평균기온 데이터 기반 회귀 알고리즘 비교 분석"
)
