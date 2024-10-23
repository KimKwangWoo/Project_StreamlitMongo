# app.py

import streamlit as st
from pymongo import MongoClient
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 글꼴 설정
font_path = "C:/Windows/Fonts/malgun.ttf"  # Windows의 경우 Malgun Gothic 경로
font_prop = fm.FontProperties(fname=font_path, size=12)
plt.rc('font', family=font_prop.get_name())

# config.json 파일에서 MongoDB 연결 정보 읽기
with open('config.json') as config_file:
    config = json.load(config_file)

# MongoDB 연결
client = MongoClient(config["mongodb_uri"])         # MongoDB URI
db = client[config["database_name"]]                # 데이터베이스 이름

# 컬렉션 선택
collection_name = config["collections"][0]  # 첫 번째 컬렉션 선택
collect_data = db[collection_name]  # 컬렉션 객체

# 가장 오래된 100개의 데이터 가져오기
data = list(collect_data.find().sort("LOG_DATE", 1).limit(100))  # LOG_DATE 기준으로 정렬하여 100개 가져오기
if not data:
    st.write("데이터가 없습니다.")
else:
    # 데이터프레임으로 변환
    df = pd.DataFrame(data)

    # _id 필드 제거
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)

    # LOG_DATE를 datetime 형식으로 변환
    if 'LOG_DATE' in df.columns:
        df['LOG_DATE'] = pd.to_datetime(df['LOG_DATE'])
    else:
        st.write("LOG_DATE 필드가 존재하지 않습니다.")

    # 필요한 열만 선택하고 이름 변경
    df_display = df[['SYS_ID', 'LOG_DATE', 'SS_SEQ', 'LOG_VAL', 'LOG_VAL_ALM_HH', 'LOG_VAL_ALM_HI', 'LOG_VAL_ALM_LO', 'LOG_VAL_ALM_LL']]
    df_display.columns = ['SYS_ID', 'DATE', 'SS_SEQ', 'VALUE', 'HH', 'HI', 'LO', 'LL']  # 열 이름 변경

    # 시각화
    st.title(f"{collection_name} 데이터 시각화")
    
    # 데이터프레임 출력
    st.write(df_display)

    # SS_SEQ별로 데이터 그룹화
    if 'SS_SEQ' in df.columns:
        grouped = df.groupby('SS_SEQ')

        # 그래프 그리기
        plt.figure(figsize=(10, 5))
        
        for name, group in grouped:
            plt.plot(group['LOG_DATE'], group['LOG_VAL'], marker='o', label=name)  # 'LOG_VAL'로 수정

        plt.title(f"{collection_name}의 SS_SEQ별 시간에 따른 값 변화")
        plt.xlabel("시간")
        plt.ylabel("값")
        plt.xticks(rotation=45)
        plt.legend(title='SS_SEQ')
        plt.tight_layout()
        st.pyplot(plt)
    else:
        st.write("SS_SEQ 필드가 존재하지 않습니다.")
