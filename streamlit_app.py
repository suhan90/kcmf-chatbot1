import streamlit as st
import requests
import os

# API 엔드포인트 : 스트림릿 환경설정 값으로 지정
API_ENDPOINT = os.environ.get("API_ENDPOINT", "https://kcmf-chatbot-api.....run.app/un.app/query")

st.title("문서 질의응답 시스템")
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

            st.write("상태 코드:", response.status_code)
            st.write("응답 헤더:", response.headers)
            st.write("응답 내용:", response.text)
            
            if response.status_code == 200:
                answer = response.json().get("answer")
                st.write("### 답변")
                st.write(answer)
            else:
                st.error(f"오류가 발생했습니다: {response.json().get('error', '알 수 없는 오류')}")
        except Exception as e:
            st.error(f"요청 중 오류가 발생했습니다: {str(e)}")
