
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# =========================================
# 1. 페이지 설정
# =========================================

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 머신러닝")
st.write(
    "꽃의 길이와 너비를 입력하고 "
    "3가지 머신러닝 알고리즘으로 품종을 예측해 보자!"
)

st.divider()


# =========================================
# 2. 데이터 불러오기
# =========================================

base_dir = Path(__file__).resolve().parent

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


features = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비"
]

target = "품종"

if not all(col in df.columns for col in features + [target]):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

df = df.dropna(subset=features + [target]).copy()


# =========================================
# 3. 알고리즘 설정
# =========================================

algorithm_names = [
    "KNN",
    "결정 트리",
    "랜덤 포레스트"
]

principles = {
    "KNN": """
### 🔍 KNN (K-최근접 이웃)

KNN은 새로운 데이터와 가장 가까운 기존 데이터를
찾아서 품종을 예측하는 알고리즘이야.

1. 사용자가 꽃의 길이와 너비를 입력해.
2. 기존 붓꽃 데이터와의 거리를 계산해.
3. 가장 가까운 5개의 데이터를 찾아.
4. 가장 많이 등장한 품종을 예측 결과로 선택해.

**핵심:** 주변에 있는 데이터의 의견을 모아서 결정하는 방법이야.
""",

    "결정 트리": """
### 🌳 결정 트리 (Decision Tree)

결정 트리는 질문을 반복하면서 데이터를 분류하는 알고리즘이야.

1. 꽃의 길이와 너비를 확인해.
2. 품종을 가장 잘 구분할 수 있는 조건을 찾아.
3. 조건에 따라 데이터를 여러 그룹으로 나눠.
4. 마지막에 도달한 그룹을 바탕으로 품종을 예측해.

**핵심:** 여러 가지 질문을 따라가면서 정답을 찾아가는 방법이야.
""",

    "랜덤 포레스트": """
### 🌲 랜덤 포레스트 (Random Forest)

랜덤 포레스트는 여러 개의 결정 트리를 사용하는 알고리즘이야.

1. 여러 개의 학습 데이터를 무작위로 구성해.
2. 각각의 데이터로 결정 트리를 만들어.
3. 여러 트리가 각각 품종을 예측해.
4. 가장 많은 트리가 선택한 품종을 최종 결과로 결정해.

**핵심:** 여러 나무의 예측 결과를 모아서 결정하는 방법이야.
"""
}


def make_model(name):

    if name == "KNN":
        return Pipeline([
            ("scaler", StandardScaler()),
            ("model", KNeighborsClassifier(n_neighbors=5))
        ])

    elif name == "결정 트리":
        return DecisionTreeClassifier(
            random_state=42
        )

    elif name == "랜덤 포레스트":
        return RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )


# =========================================
# 4. 공통 예측 함수
# =========================================

def prediction_app(tab_name, selected_features, algorithm_key):

    st.subheader("🤖 예측 알고리즘 선택")

    algorithm = st.selectbox(
        "사용할 분류 알고리즘을 선택해 줘!",
        algorithm_names,
        key=algorithm_key
    )

    st.caption(
        "알고리즘에 따라 예측 결과와 정확도가 달라질 수 있어."
    )

    # 입력창
    st.subheader("✏️ 꽃의 크기 입력하기")

    col1, col2 = st.columns(2)

    input_values = []

    for i, feature in enumerate(selected_features):

        minimum = float(df[feature].min())
        maximum = float(df[feature].max())
        default = float(df[feature].median())

        with (col1 if i == 0 else col2):

            value = st.number_input(
                f"{feature} (cm)",
                min_value=minimum,
                max_value=maximum,
                value=default,
                step=0.1,
                format="%.1f",
                key=f"{tab_name}_{feature}"
            )

            st.caption(
                f"입력 가능 범위: {minimum} ~ {maximum} cm"
            )

            input_values.append(value)

    input_data = pd.DataFrame(
        [input_values],
        columns=selected_features
    )

    # =====================================
    # 5. 학습 및 정확도 비교
    # =====================================

    X = df[selected_features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    accuracies = {}
    trained_models = {}

    for name in algorithm_names:

        temp_model = make_model(name)

        temp_model.fit(X_train, y_train)

        test_prediction = temp_model.predict(X_test)

        accuracies[name] = accuracy_score(
            y_test,
            test_prediction
        ) * 100

        trained_models[name] = temp_model

    st.divider()

    # =====================================
    # 6. 예측 결과
    # =====================================

    st.subheader("🌸 붓꽃 품종 예측 결과")

    final_model = make_model(algorithm)

    final_model.fit(X, y)

    prediction = final_model.predict(input_data)[0]

    col1, col2 = st.columns(2)

    with col1:
        st.success(f"예측 품종: {prediction}")

        if prediction == "Iris-setosa":
            st.markdown("### 🌼 Iris-setosa")
            st.write("세토사 품종으로 예측했어!")

        elif prediction == "Iris-versicolor":
            st.markdown("### 🌺 Iris-versicolor")
            st.write("버시컬러 품종으로 예측했어!")

        elif prediction == "Iris-virginica":
            st.markdown("### 🌷 Iris-virginica")
            st.write("버지니카 품종으로 예측했어!")

    with col2:
        st.metric(
            "선택한 알고리즘의 테스트 정확도",
            f"{accuracies[algorithm]:.1f}%"
        )

    # 알고리즘별 정확도 비교
    st.subheader("📊 알고리즘별 정확도 비교")

    accuracy_df = pd.DataFrame({
        "알고리즘": list(accuracies.keys()),
        "정확도 (%)": list(accuracies.values())
    })

    st.dataframe(
        accuracy_df,
        use_container_width=True,
        hide_index=True
    )

    accuracy_fig = px.bar(
        accuracy_df,
        x="알고리즘",
        y="정확도 (%)",
        color="알고리즘",
        text="정확도 (%)",
        title="분류 알고리즘별 테스트 정확도"
    )

    accuracy_fig.update_traces(
        texttemplate="%{y:.1f}%",
        textposition="outside"
    )

    accuracy_fig.update_layout(
        yaxis_range=[0, 110],
        showlegend=False
    )

    st.plotly_chart(
        accuracy_fig,
        use_container_width=True
    )

    # =====================================
    # 7. 산점도
    # =====================================

    st.divider()

    st.subheader("📍 붓꽃 데이터 산점도")

    st.write(
        f"가로축: {selected_features[0]} / "
        f"세로축: {selected_features[1]}"
    )

    fig = px.scatter(
        df,
        x=selected_features[0],
        y=selected_features[1],
        color=target,
        hover_data=selected_features,
        title="붓꽃 품종별 데이터 분포"
    )

    # 사용자 입력값: 하늘색 별
    fig.add_scatter(
        x=[input_values[0]],
        y=[input_values[1]],
        mode="markers",
        name="내가 입력한 꽃",
        marker=dict(
            symbol="star",
            size=23,
            color="skyblue",
            line=dict(
                color="black",
                width=1
            )
        )
    )

    fig.update_layout(
        height=550,
        xaxis_title=f"{selected_features[0]} (cm)",
        yaxis_title=f"{selected_features[1]} (cm)",
        legend_title="붓꽃 품종"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "⭐ 하늘색 별은 사용자가 입력한 꽃의 위치야."
    )

    # =====================================
    # 8. 알고리즘 작동 원리
    # =====================================

    st.divider()

    st.subheader("💡 선택한 알고리즘의 작동 원리")

    st.markdown(principles[algorithm])

    with st.expander("📚 다른 알고리즘의 작동 원리도 알아보기"):

        for name in algorithm_names:
            st.markdown(principles[name])
            st.divider()


# =========================================
# 9. 탭 구성
# =========================================

tab1, tab2 = st.tabs([
    "🌷 꽃잎 길이와 너비로 예측",
    "🌿 원하는 속성 2개로 예측"
])


# =========================================
# 탭 1
# =========================================

with tab1:

    st.header("🌷 꽃잎 크기로 품종 예측하기")

    st.write(
        "기존에 사용했던 꽃잎 길이와 꽃잎 너비를 "
        "이용해서 붓꽃의 품종을 예측해 보자!"
    )

    prediction_app(
        tab_name="petal",
        selected_features=[
            "꽃잎 길이",
            "꽃잎 너비"
        ],
        algorithm_key="algorithm_petal"
    )


# =========================================
# 탭 2
# =========================================

with tab2:

    st.header("🌿 원하는 속성 2개 선택하기")

    st.write(
        "이번에는 꽃받침과 꽃잎의 네 가지 속성 중 "
        "원하는 두 가지를 골라서 품종을 예측해 보자!"
    )

    st.info(
        "서로 다른 두 가지 속성을 선택해야 해. "
        "선택한 속성에 따라 입력 범위와 그래프의 축도 바뀌어."
    )

    col1, col2 = st.columns(2)

    with col1:

        feature_x = st.selectbox(
            "📌 첫 번째 속성 선택",
            features,
            index=0,
            key="feature_x"
        )

    with col2:

        available_features = [
            f for f in features if f != feature_x
        ]

        feature_y = st.selectbox(
            "📌 두 번째 속성 선택",
            available_features,
            index=0,
            key="feature_y"
        )

    st.success(
        f"선택한 속성: {feature_x} + {feature_y}"
    )

    prediction_app(
        tab_name="custom",
        selected_features=[
            feature_x,
            feature_y
        ],
        algorithm_key="algorithm_custom"
    )


# =========================================
# 10. 데이터 안내
# =========================================

st.divider()

with st.expander("📖 원본 Iris 데이터 확인"):

    st.dataframe(
        df,
        use_container_width=True
    )

    st.write("전체 데이터 개수:", len(df))

    st.write(
        "품종 종류:",
        df[target].unique().tolist()
    )

st.caption(
    "🌸 Iris 데이터 기반 붓꽃 품종 머신러닝 예측 프로그램"
)
