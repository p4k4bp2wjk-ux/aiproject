
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write("붓꽃의 여러 특징을 입력하고 머신러닝 알고리즘으로 품종을 예측해 보세요!")
st.divider()


# --------------------------------------------------
# 2. CSV 파일 불러오기
# --------------------------------------------------

base_dir = Path(__file__).resolve().parent

file_path = base_dir.parent / "Iris.csv"

if not file_path.exists():
    file_path = base_dir / "Iris.csv"

if not file_path.exists():
    st.error("Iris.csv 파일을 찾을 수 없습니다. CSV 파일의 위치를 확인해 주세요.")
    st.stop()

try:
    df = pd.read_csv(file_path, encoding="cp949")
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding="utf-8-sig")


# --------------------------------------------------
# 3. 데이터 확인
# --------------------------------------------------

features = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비"
]

target = "품종"

missing_columns = [
    col for col in features + [target]
    if col not in df.columns
]

if missing_columns:
    st.error(
        "CSV 파일에 필요한 열이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.write("현재 CSV 파일의 열 이름:", df.columns.tolist())
    st.stop()

df = df[features + [target]].copy()

for col in features:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna()

if len(df) < 10:
    st.error("분석할 데이터가 너무 적습니다.")
    st.stop()

X = df[features]
y = df[target]

species = sorted(y.unique())


# --------------------------------------------------
# 4. 머신러닝 알고리즘 만들기
# --------------------------------------------------

algorithm_names = [
    "KNN",
    "결정 트리",
    "랜덤 포레스트"
]


def make_model(name):

    if name == "KNN":
        return make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=5)
        )

    elif name == "결정 트리":
        return DecisionTreeClassifier(
            random_state=42
        )

    elif name == "랜덤 포레스트":
        return RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )


principles = {
    "KNN": """
    ### 📍 KNN 알고리즘

    KNN은 새롭게 입력된 데이터와 기존 데이터 사이의 거리를 계산합니다.

    가장 가까운 5개의 데이터를 확인한 뒤,
    주변에서 가장 많이 나타나는 품종으로 예측합니다.
    """,

    "결정 트리": """
    ### 🌳 결정 트리 알고리즘

    결정 트리는 여러 가지 질문을 통해 데이터를 분류합니다.

    예를 들어 꽃잎 길이가 특정 값보다 긴지 짧은지 등을
    차례대로 판단하여 품종을 예측합니다.
    """,

    "랜덤 포레스트": """
    ### 🌲 랜덤 포레스트 알고리즘

    랜덤 포레스트는 여러 개의 결정 트리를 만들어 예측합니다.

    각각의 결정 트리가 예측한 결과를 모아
    가장 많이 선택된 품종을 최종 결과로 결정합니다.
    """
}


# --------------------------------------------------
# 5. 예측 프로그램 함수
# --------------------------------------------------

def prediction_app(tab_name, selected_features):

    st.subheader("🔎 붓꽃 특징 입력하기")

    st.write(
        "아래에서 꽃의 특징을 입력하면 "
        "세 가지 알고리즘이 각각 품종을 예측합니다."
    )

    col1, col2 = st.columns(2)

    input_values = {}

    for i, feature in enumerate(selected_features):

        min_value = float(df[feature].min())
        max_value = float(df[feature].max())
        default_value = float(df[feature].median())

        with (col1 if i == 0 else col2):

            input_values[feature] = st.number_input(
                feature,
                min_value=min_value,
                max_value=max_value,
                value=default_value,
                step=0.1,
                format="%.2f",
                key=f"{tab_name}_{feature}"
            )

            st.caption(
                f"데이터 범위: {min_value:.2f} ~ {max_value:.2f}"
            )

    input_data = pd.DataFrame(
        [[input_values[f] for f in selected_features]],
        columns=selected_features
    )

    st.divider()

    # 선택한 두 가지 특징만 학습에 사용
    X_selected = df[selected_features]

    # 학습 데이터와 테스트 데이터 나누기
    X_train, X_test, y_train, y_test = train_test_split(
        X_selected,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # --------------------------------------------------
    # 6. 세 가지 알고리즘의 정확도와 예측 결과 계산
    # --------------------------------------------------

    results = []
    accuracy_results = []
    prediction_counts = {}

    for name in algorithm_names:

        # 정확도 평가용 모델
        evaluation_model = make_model(name)

        evaluation_model.fit(X_train, y_train)

        test_prediction = evaluation_model.predict(X_test)

        accuracy = accuracy_score(
            y_test,
            test_prediction
        )

        accuracy_results.append({
            "알고리즘": name,
            "정확도": accuracy * 100
        })

        # 입력한 꽃의 품종 예측용 모델
        prediction_model = make_model(name)

        prediction_model.fit(X_selected, y)

        predicted_species = prediction_model.predict(
            input_data
        )[0]

        results.append({
            "알고리즘": name,
            "예측 품종": predicted_species,
            "정확도": round(accuracy * 100, 2)
        })

        prediction_counts[predicted_species] = (
            prediction_counts.get(predicted_species, 0) + 1
        )

    # --------------------------------------------------
    # 7. 세 가지 알고리즘 예측 결과 비교
    # --------------------------------------------------

    st.subheader("🤖 알고리즘별 예측 결과")

    result_cols = st.columns(3)

    for i, result in enumerate(results):

        with result_cols[i]:

            st.markdown(f"#### {result['알고리즘']}")

            st.success(
                f"🌸 {result['예측 품종']}"
            )

            st.metric(
                "테스트 정확도",
                f"{result['정확도']:.2f}%"
            )

    result_df = pd.DataFrame(results)

    st.markdown("#### 📋 예측 결과 비교표")

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    # 가장 많이 예측된 품종 확인
    max_count = max(prediction_counts.values())

    most_common = [
        name for name, count in prediction_counts.items()
        if count == max_count
    ]

    if len(most_common) == 1:
        st.info(
            f"💡 세 알고리즘 중 가장 많은 예측 결과는 "
            f"**{most_common[0]}**입니다. "
            f"({max_count}/3개 알고리즘)"
        )
    else:
        st.info(
            "💡 여러 알고리즘의 예측 결과가 나뉘었습니다. "
            "아래 그래프에서 결과를 비교해 보세요."
        )

    # --------------------------------------------------
    # 8. 예측 품종 개수 그래프
    # --------------------------------------------------

    st.markdown("#### 📊 알고리즘별 품종 예측 개수")

    count_df = pd.DataFrame({
        "예측 품종": list(prediction_counts.keys()),
        "예측 개수": list(prediction_counts.values())
    })

    count_fig = px.bar(
        count_df,
        x="예측 품종",
        y="예측 개수",
        color="예측 품종",
        text="예측 개수",
        title="세 가지 알고리즘의 예측 결과"
    )

    count_fig.update_layout(
        yaxis=dict(
            dtick=1,
            range=[0, 3.5]
        ),
        showlegend=False
    )

    st.plotly_chart(
        count_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # 9. 알고리즘 정확도 비교 그래프
    # --------------------------------------------------

    st.markdown("#### 🏆 알고리즘별 정확도 비교")

    accuracy_df = pd.DataFrame(accuracy_results)

    accuracy_fig = px.bar(
        accuracy_df,
        x="알고리즘",
        y="정확도",
        color="알고리즘",
        text="정확도",
        title="테스트 데이터 기준 정확도 비교"
    )

    accuracy_fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    accuracy_fig.update_layout(
        yaxis_title="정확도 (%)",
        xaxis_title="알고리즘",
        yaxis_range=[
            0,
            min(110, max(100, accuracy_df["정확도"].max() + 10))
        ],
        showlegend=False
    )

    st.plotly_chart(
        accuracy_fig,
        use_container_width=True
    )

    st.caption(
        "※ 정확도는 전체 데이터 중 20%를 테스트 데이터로 나누어 "
        "평가한 결과입니다. 데이터 분할에 따라 값이 달라질 수 있습니다."
    )

    st.divider()

    # --------------------------------------------------
    # 10. 산점도
    # --------------------------------------------------

    st.subheader("📈 붓꽃 데이터 산점도")

    scatter_df = df.copy()

    fig = px.scatter(
        scatter_df,
        x=selected_features[0],
        y=selected_features[1],
        color=target,
        title=(
            f"{selected_features[0]}과 "
            f"{selected_features[1]}에 따른 붓꽃 품종"
        ),
        hover_data=features
    )

    # 사용자가 입력한 데이터 표시
    fig.add_trace(
        go.Scatter(
            x=[input_values[selected_features[0]]],
            y=[input_values[selected_features[1]]],
            mode="markers",
            name="내가 입력한 꽃",
            marker=dict(
                color="skyblue",
                size=18,
                symbol="star",
                line=dict(
                    color="black",
                    width=1
                )
            )
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # 11. 알고리즘 원리 설명
    # --------------------------------------------------

    st.subheader("📚 알고리즘 작동 원리 알아보기")

    selected_algorithm = st.selectbox(
        "설명을 확인할 알고리즘을 선택하세요.",
        algorithm_names,
        key=f"{tab_name}_algorithm_explanation"
    )

    st.markdown(
        principles[selected_algorithm]
    )


# --------------------------------------------------
# 12. 탭 구성
# --------------------------------------------------

tab1, tab2 = st.tabs([
    "🌷 꽃잎 길이와 너비로 예측하기",
    "🌼 원하는 특징 2개로 예측하기"
])


# 첫 번째 탭
with tab1:

    st.write(
        "꽃잎 길이와 꽃잎 너비를 이용하여 "
        "붓꽃의 품종을 예측합니다."
    )

    prediction_app(
        "petal",
        ["꽃잎 길이", "꽃잎 너비"]
    )


# 두 번째 탭
with tab2:

    st.write(
        "네 가지 특징 중 원하는 두 가지를 선택하여 "
        "붓꽃의 품종을 예측합니다."
    )

    select_col1, select_col2 = st.columns(2)

    with select_col1:
        feature1 = st.selectbox(
            "첫 번째 특징",
            features,
            index=0,
            key="custom_feature1"
        )

    with select_col2:
        feature2 = st.selectbox(
            "두 번째 특징",
            features,
            index=1,
            key="custom_feature2"
        )

    if feature1 == feature2:

        st.warning(
            "서로 다른 특징 두 가지를 선택해 주세요."
        )

    else:

        prediction_app(
            "custom",
            [feature1, feature2]
        )


# --------------------------------------------------
# 13. 데이터 확인
# --------------------------------------------------

with st.expander("📂 사용한 붓꽃 데이터 확인하기"):

    st.write(f"전체 데이터 개수: {len(df)}개")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.write("품종별 데이터 개수")

    st.dataframe(
        df[target].value_counts().rename("개수"),
        use_container_width=True
    )
