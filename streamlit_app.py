import streamlit as st
import requests
import os

# API 엔드포인트 (Cloud Functions 또는 Cloud Run에 배포된 주소)
API_ENDPOINT = os.environ.get("API_ENDPOINT", "https://kcmf-chatbot-api.....run.app/un.app/query")

st.title("문서 질의응답 시스템")
st.write(API_ENDPOINT)
st.write("문서 관련 질문을 입력하면 관련 문서에서 답변을 찾아드립니다.")

# 사용자 입력
question = st.text_input("질문:")

if question:
    with st.spinner("답변을 찾고 있습니다..."):
        try:
            response = requests.post(
                API_ENDPOINT,
                json={"question": question}
            )
            
            if response.status_code == 200:
                answer = response.json().get("answer")
                st.write("### 답변")
                st.write(answer)
            else:
                st.error(f"오류가 발생했습니다: {response.json().get('error', '알 수 없는 오류')}")
        except Exception as e:
            st.error(f"요청 중 오류가 발생했습니다: {str(e)}")
