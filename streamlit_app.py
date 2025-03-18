import streamlit as st
import requests
import os

# API 엔드포인트 (App Engine 또는 Cloud Run에 배포된 주소)
API_URL = os.environ.get("API_URL")

st.set_page_config(
    page_title="PDF 문서 질의응답 시스템",
    page_icon="📚",
    layout="wide"
)

st.title("문서 질의응답 시스템")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바
with st.sidebar:
    st.header("사용 안내")
    st.write("""
    문서 관련 질문을 입력하면 관련 문서에서 답변을 찾아드립니다.
    """)
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.experimental_rerun()

# 기존 대화 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력
# question = st.text_input("질문:")
question = st.chat_input("질문:")

if question:
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(question)
    
    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": question})

    # 로딩 표시
    with st.chat_message("assistant"):
        with st.spinner("답변 찾는 중..."):
            try:
                 # API 호출
                response = requests.post(
                    API_URL,
                    json={"question": question}
                )
                response.raise_for_status() # 오류 발생 시 예외 처리

                # 응답 표시 및 저장
                answer = response.json().get("answer", "응답을 받지 못했습니다.")
                st.write("### 답변")
                st.write(answer)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer
                })

            except requests.RequestException as e:
                st.error(f"API 요청 오류: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_detail = e.response.json()
                        st.error(f"세부 오류: {error_detail.get('detail', '알 수 없는 오류')}")
                    except:
                        st.error(f"상태 코드: {e.response.status_code}")
