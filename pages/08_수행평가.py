
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------
# 1. 기본 설정
# ---------------------------------

st.set_page_config(
    page_title="KBL 구단 전력 분석",
    page_icon="🏀",
    layout="wide"
)

RED = "#C62828"
RED_LIGHT = "#F3A6A6"
RED_DARK = "#8E0000"

st.title("🏀 KBL 구단 전력 분석 시스템")
st.caption("KBL 10개 구단의 시즌 성적과 세부 기록을 분석해 보세요!")


# ---------------------------------
# 2. CSV 파일 불러오기
# ---------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT_DIR / "kbl_integrated_team_game_data.csv"

TEAM_COLS = [
    "구단",
    "시즌_경기수",
    "시즌_승리",
    "시즌_패배",
    "시즌_승률",
    "경기당_득점",
    "경기당_실점",
    "경기당_득실차",
    "야투성공률_pct",
    "경기당_3점슛성공",
    "3점슛성공률_pct",
    "자유투성공률_pct",
    "경기당_리바운드",
    "경기당_어시스트",
    "경기당_스틸",
    "경기당_블록",
    "경기당_턴오버",
    "홈_승리",
    "홈_패배",
    "원정_승리",
    "원정_패배"
]


@st.cache_data
def load_data():

    data = pd.read_csv(
        DATA_FILE,
        encoding="utf-8-sig"
    )

    data["날짜"] = pd.to_datetime(data["날짜"])

    standings = data[TEAM_COLS].drop_duplicates(
        "구단"
    ).copy()

    games = data[data["홈원정"] == "홈"][
        [
            "날짜",
            "구단",
            "상대구단",
            "팀득점",
            "상대득점",
            "경기결과"
        ]
    ].copy()

    games.columns = [
        "날짜",
        "홈팀",
        "원정팀",
        "홈팀점수",
        "원정팀점수",
        "홈팀결과"
    ]

    games["승리팀"] = games.apply(
        lambda r: r["홈팀"]
        if r["홈팀점수"] > r["원정팀점수"]
        else r["원정팀"],
        axis=1
    )

    return data, standings, games


try:

    data, standings, games = load_data()

except FileNotFoundError:

    st.error(
        "통합 CSV 파일을 찾을 수 없습니다. "
        "프로젝트 최상위 폴더에 "
        "kbl_integrated_team_game_data.csv를 넣어 주세요."
    )

    st.stop()


st.info(
    "자료 기준일: 2026년 11월 19일 | "
    "시즌 성적과 경기당 평균 기록 및 "
    "2026년 11월 1일~19일 경기 결과를 포함합니다."
)


# ---------------------------------
# 3. 구단 선택
# ---------------------------------

team = st.selectbox(
    "분석할 구단을 선택하세요.",
    standings["구단"].tolist()
)

row = standings[
    standings["구단"] == team
].iloc[0]

team_games = data[
    data["구단"] == team
].sort_values(
    "날짜",
    ascending=False
).copy()


# ---------------------------------
# 4. 시즌 성적
# ---------------------------------

st.subheader(f"📌 {team} 시즌 성적")

a, b, c, d = st.columns(4)

a.metric(
    "경기 수",
    f'{int(row["시즌_경기수"])}경기'
)

b.metric(
    "승리",
    f'{int(row["시즌_승리"])}승'
)

c.metric(
    "패배",
    f'{int(row["시즌_패배"])}패'
)

d.metric(
    "승률",
    f'{row["시즌_승률"] * 100:.1f}%'
)


# ---------------------------------
# 5. 팀 세부 기록
# ---------------------------------

st.subheader("📊 팀 세부 기록")

st.caption("아래 수치는 경기당 평균 또는 성공률입니다.")

metrics = [
    ("득점", "경기당_득점", "점"),
    ("실점", "경기당_실점", "점"),
    ("리바운드", "경기당_리바운드", "개"),
    ("어시스트", "경기당_어시스트", "개"),
    ("스틸", "경기당_스틸", "개"),
    ("블록", "경기당_블록", "개"),
    ("턴오버", "경기당_턴오버", "개"),
    ("득실 차", "경기당_득실차", "점")
]

metric_cols = st.columns(4)

for i, (label, col, unit) in enumerate(metrics):

    metric_cols[i % 4].metric(
        label,
        f'{row[col]:.1f}{unit}'
    )


# ---------------------------------
# 6. 슛 성공률 그래프
# ---------------------------------

st.subheader("🎯 슛 성공률 분석")

shooting = pd.DataFrame({
    "기록": [
        "야투 성공률",
        "3점슛 성공률",
        "자유투 성공률"
    ],

    "성공률(%)": [
        row["야투성공률_pct"],
        row["3점슛성공률_pct"],
        row["자유투성공률_pct"]
    ]
})

fig_shoot = px.bar(
    shooting,
    x="기록",
    y="성공률(%)",
    text="성공률(%)",
    color_discrete_sequence=[RED],
    title=f"{team} 슛 성공률"
)

fig_shoot.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig_shoot.update_layout(
    yaxis_range=[0, 100],
    xaxis_title="",
    yaxis_title="성공률(%)"
)

st.plotly_chart(
    fig_shoot,
    use_container_width=True
)


# ---------------------------------
# 7. 최근 경기 분석
# ---------------------------------

st.divider()

st.subheader("1. 🏀 최근 경기 결과")

if team_games.empty:

    st.warning(
        "해당 구단의 경기 결과가 없습니다."
    )

else:

    nmax = min(10, len(team_games))

    n = st.slider(
        "최근 경기 몇 개를 볼까요?",
        1,
        nmax,
        min(5, nmax)
    )

    recent = team_games.head(n).copy()

    wins = int(
        (recent["경기결과"] == "승").sum()
    )

    losses = n - wins

    x, y, z = st.columns(3)

    x.metric(
        f"최근 {n}경기 승리",
        f"{wins}승"
    )

    y.metric(
        f"최근 {n}경기 패배",
        f"{losses}패"
    )

    z.metric(
        "최근 경기 승률",
        f"{wins / n * 100:.1f}%"
    )


    # 최근 경기 득점 비교

    score_chart = recent.melt(
        id_vars=[
            "날짜",
            "상대구단"
        ],

        value_vars=[
            "팀득점",
            "상대득점"
        ],

        var_name="구분",
        value_name="점수"
    )

    score_chart["구분"] = score_chart[
        "구분"
    ].map({
        "팀득점": team,
        "상대득점": "상대 구단"
    })

    score_chart["경기"] = (
        score_chart["날짜"].dt.strftime("%m/%d")
        + " vs "
        + score_chart["상대구단"]
    )

    fig = px.bar(
        score_chart,
        x="경기",
        y="점수",
        color="구분",
        barmode="group",
        text="점수",

        color_discrete_map={
            team: RED_DARK,
            "상대 구단": RED_LIGHT
        },

        title="최근 경기 득점 비교"
    )

    fig.update_layout(
        xaxis_title="",
        yaxis_title="점수",
        xaxis_tickangle=-25,
        legend_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # 경기 상세 기록

    st.markdown("#### 최근 경기 상세 기록")

    detail = recent[
        [
            "날짜",
            "상대구단",
            "홈원정",
            "팀득점",
            "상대득점",
            "경기결과"
        ]
    ].copy()

    detail["날짜"] = detail[
        "날짜"
    ].dt.strftime("%Y-%m-%d")

    detail.columns = [
        "날짜",
        "상대 구단",
        "홈/원정",
        "우리 팀 득점",
        "상대 득점",
        "결과"
    ]

    st.dataframe(
        detail,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------
# 8. 구단별 승률 비교
# ---------------------------------

st.divider()

st.subheader("2. 📈 10개 구단 시즌 전력 비교")

rank = standings.sort_values(
    "시즌_승률",
    ascending=False
).copy()

rank["구분"] = rank["구단"].apply(
    lambda x:
    "선택 구단" if x == team else "다른 구단"
)

fig_rank = px.bar(
    rank,
    x="구단",
    y="시즌_승률",
    color="구분",
    text="시즌_승률",

    color_discrete_map={
        "선택 구단": RED_DARK,
        "다른 구단": RED_LIGHT
    },

    title="KBL 구단별 승률 비교"
)

fig_rank.update_traces(
    texttemplate="%{text:.3f}",
    textposition="outside"
)

fig_rank.update_layout(
    xaxis_title="",
    yaxis_title="승률",
    xaxis_tickangle=-30,
    legend_title=""
)

st.plotly_chart(
    fig_rank,
    use_container_width=True
)


# ---------------------------------
# 9. 세부 기록 비교
# ---------------------------------

st.subheader("3. 🔍 구단별 세부 기록 비교")

compare_cols = [
    "경기당_득점",
    "경기당_리바운드",
    "경기당_어시스트"
]

compare_labels = {
    "경기당_득점": "경기당 득점",
    "경기당_리바운드": "경기당 리바운드",
    "경기당_어시스트": "경기당 어시스트"
}

selected_stat = st.selectbox(
    "비교할 세부 기록을 선택하세요.",
    compare_cols,
    format_func=lambda x: compare_labels[x]
)

fig_compare = px.bar(
    standings.sort_values(
        selected_stat,
        ascending=False
    ),

    x="구단",
    y=selected_stat,
    text=selected_stat,

    color_discrete_sequence=[RED],

    title=compare_labels[selected_stat] + " 구단별 비교"
)

fig_compare.update_layout(
    xaxis_title="",
    yaxis_title="경기당 평균",
    xaxis_tickangle=-30
)

st.plotly_chart(
    fig_compare,
    use_container_width=True
)


# ---------------------------------
# 10. 통합 데이터 확인
# ---------------------------------

st.divider()

st.subheader("4. 📋 통합 데이터 미리보기")

st.caption(
    "한 행은 한 경기에서 한 구단이 기록한 내용이며, "
    "해당 구단의 시즌 성적과 세부 기록도 함께 표시됩니다."
)

st.dataframe(
    data.sort_values(
        ["구단", "날짜"],
        ascending=[True, False]
    ),
    use_container_width=True,
    hide_index=True
)


# ---------------------------------
# 11. 데이터 출처
# ---------------------------------

st.caption(
    "출처: KBL 공식 팀 순위 및 경기 일정·결과. "
    "자료 기준일: 2026년 11월 19일."
)

