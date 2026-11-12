
from pathlib import Path
import streamlit as st
import pandas as pd

# 현재 실행 파일 기준 상위 폴더
BASE_DIR = Path(__file__).resolve().parent.parent

st.write("현재 파이썬 파일:", __file__)
st.write("검색하는 폴더:", str(BASE_DIR))
st.write("상위 폴더 파일 목록:")

for file in BASE_DIR.iterdir():
    st.write(file.name)

# CSV 파일 찾기
CSV_PATH = BASE_DIR / "temperature(1).csv"

if not CSV_PATH.is_file():
    st.error(f"파일을 찾을 수 없습니다: {CSV_PATH}")
    st.stop()

df = pd.read_csv(CSV_PATH, encoding="cp949")

st.success("CSV 파일 불러오기 성공!")
st.dataframe(df.head())
