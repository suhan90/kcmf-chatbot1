import streamlit as st
import requests
import os

# API 엔드포인트 (App Engine 또는 Cloud Run에 배포된 주소)
API_URL = os.environ.get("API_URL")
# 암호
ACCESS_PASSWORD = os.environ.get("ACCESS_PASSWORD")

st.set_page_config(
    page_title="KCMF문서 Q&A 챗봇",
    page_icon="📚",
    layout="wide"
)

st.title("KCMF문서 Q&A 챗봇")

# 로그인 여부 확인
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    # 엔터키 처리를 위해 form 사용
    with st.form(key='password_form'):
        password = st.text_input("암호를 입력하세요:", type="password", key="password_input")
        submit_button = st.form_submit_button("확인")
        if submit_button:
            if password == ACCESS_PASSWORD:
                st.session_state.authenticated = True
                st.success("인증 성공!")
                st.rerun() # 화면을 다시 렌더링하여 암호 입력창을 제거
            else:
                st.warning("잘못된 암호입니다.")
                # st.error("잘못된 암호입니다.")
    
if not st.session_state.authenticated:
    st.stop()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바
with st.sidebar:
    st.header("안내")
    st.write("""
    #### 입력된 자료:\n
    - 재단 규정, 규칙, 지침, 절차서, 매뉴얼, 마디어교육 연구보고서, 교재 등\n
    - 업무자료 주시면 추가합니다. 자료 만들기가 중요!\n
    #### 질문 예시:\n
    - 보호자가 아이에게 스마트폰을 주는 이유?\n
    - OOO 강사 전화, 이메일, 소득 구분\n
    - 강사 평가를 위해 직원이 해야 하는 일?
    - 울산센터, 부산센터의 마을미디어교육 예산을 비교해줘
    - 부산센터 위기 상황 OOO 직원의 역할은?\n
    - 재단의 CCTV 갯수는?\n
    - 공문서 작성 시 1,2,3 앞에 띄어쓰기는 몇 칸?\n
    """)
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

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
                st.write("#### 답변")
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
