
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# ---------------------------------
# 1. 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측 🌸",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 붓꽃의 품종을 예측해 줘!")

st.divider()

# ---------------------------------
# 2. CSV 파일 불러오기
# ---------------------------------
base_dir = Path(__file__).resolve().parent

# 현재 폴더 또는 상위 폴더에서 CSV 찾기
file_paths = [
    base_dir / "Iris.csv",
    base_dir.parent / "Iris.csv"
]

csv_path = next(
    (p for p in file_paths if p.exists()),
    None
)

if csv_path is None:
    st.error("Iris.csv 파일을 찾을 수 없습니다.")
    st.stop()

try:
    df = pd.read_csv(csv_path, encoding="cp949")
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

# 필요한 열 확인
required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

# ---------------------------------
# 3. 학습 데이터 준비
# ---------------------------------
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# 학습용 데이터와 테스트용 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# KNN 모델 생성
model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

# 모델 학습 및 정확도 확인
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# 전체 데이터로 최종 모델 학습
model.fit(X, y)

# ---------------------------------
# 4. 알고리즘 설명
# ---------------------------------
st.subheader("🤖 사용 알고리즘")

st.info("""
**KNN (K-최근접 이웃 분류 알고리즘)**

입력한 꽃잎의 길이와 너비를 기존 데이터와 비교해
가장 가까운 5개의 데이터를 찾고,
그중 가장 많은 품종을 예측 결과로 선택해.
""")

st.metric(
    "모델 테스트 정확도",
    f"{accuracy * 100:.1f}%"
)

st.caption("테스트 데이터 20%를 이용한 정확도이며, 데이터 분할에 따라 달라질 수 있어.")

st.divider()

# ---------------------------------
# 5. 사용자 입력
# ---------------------------------
st.subheader("✏️ 꽃잎 크기 입력하기")

# 실제 데이터의 최솟값과 최댓값
length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

st.write("다음 범위 안에서 꽃잎 크기를 입력해 줘!")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=4.5,
        step=0.1,
        format="%.1f"
    )

    st.caption(
        f"입력 가능 범위: {length_min} ~ {length_max} cm"
    )

with col2:
    petal_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=1.5,
        step=0.1,
        format="%.1f"
    )

    st.caption(
        f"입력 가능 범위: {width_min} ~ {width_max} cm"
    )

# ---------------------------------
# 6. 품종 예측
# ---------------------------------
st.divider()

if st.button("🔍 붓꽃 품종 예측하기", use_container_width=True):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    prediction = model.predict(input_data)[0]

    st.success("🎉 붓꽃 품종 예측이 완료되었어!")

    st.markdown("### 🌸 예측 결과")

    if prediction == "Iris-setosa":
        st.subheader("🌼 Iris-setosa")
        st.write("예측 품종: 세토사")

    elif prediction == "Iris-versicolor":
        st.subheader("🌺 Iris-versicolor")
        st.write("예측 품종: 버시컬러")

    elif prediction == "Iris-virginica":
        st.subheader("🌷 Iris-virginica")
        st.write("예측 품종: 버지니카")

    else:
        st.subheader(prediction)

    st.write(f"입력한 꽃잎 길이: {petal_length} cm")
    st.write(f"입력한 꽃잎 너비: {petal_width} cm")

# ---------------------------------
# 7. 산점도 그래프
# ---------------------------------
st.divider()

st.subheader("📊 붓꽃 데이터 분포 그래프")

st.write("""
가로축은 꽃잎 길이, 세로축은 꽃잎 너비야.
기존 붓꽃 데이터는 품종별로 표시하고,
내가 입력한 꽃은 하늘색 별(★)로 표시해.
""")

fig = px.scatter(
    df,
    x="꽃잎 길이",
    y="꽃잎 너비",
    color="품종",
    hover_data=["꽃잎 길이", "꽃잎 너비"],
    title="붓꽃 품종별 꽃잎 크기 분포",
    labels={
        "꽃잎 길이": "꽃잎 길이 (cm)",
        "꽃잎 너비": "꽃잎 너비 (cm)"
    }
)

# 사용자가 입력한 값 표시
fig.add_scatter(
    x=[petal_length],
    y=[petal_width],
    mode="markers",
    name="내가 입력한 꽃",
    marker=dict(
        symbol="star",
        size=22,
        color="skyblue",
        line=dict(color="black", width=1)
    )
)

fig.update_layout(
    height=550,
    xaxis_title="꽃잎 길이 (cm)",
    yaxis_title="꽃잎 너비 (cm)",
    legend_title="붓꽃 품종"
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "⭐ 하늘색 별은 사용자가 입력한 꽃의 위치야."
)

# ---------------------------------
# 8. 데이터 안내
# ---------------------------------
with st.expander("📚 붓꽃 데이터 자세히 보기"):
    st.dataframe(df, use_container_width=True)

    st.write("전체 데이터 개수:", len(df))
    st.write("붓꽃 품종:", df["품종"].unique().tolist())

    st.write("꽃잎 길이 범위:", length_min, "~", length_max)
    st.write("꽃잎 너비 범위:", width_min, "~", width_max)

st.divider()

st.caption("🌸 Iris 데이터 기반 머신러닝 품종 예측 프로그램")
