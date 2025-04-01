import streamlit as st
import requests
import os
import random

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

# 질문 예시
example_questions = [
    "재단 규정, 규칙, 지침, 절차서, 매뉴얼, 마디어교육 연구보고서, 교재 등",
    "업무자료 주시면 추가합니다. 자료 만들기가 중요!",
    "보호자가 아이에게 스마트폰을 주는 이유?",
    "OOO 강사 전화, 이메일, 소득 구분",
    "강사 평가를 위해 직원이 해야 하는 일?",
    "울산센터, 부산센터의 마을미디어교육 예산을 비교해줘",
    "부산센터 위기 상황 OOO 직원의 역할은?",
    "재단의 CCTV 갯수는?",
    "공문서 작성 시 1,2,3 앞에 띄어쓰기는 몇 칸?",
    "연간 예산 계획을 수립할 때 고려해야 할 사항은?",
    "사내 교육 프로그램 운영 절차는?",
    "비영리 조직에서 기부금 사용 규정",
    "직원 채용 시 검토해야 할 필수 문서",
    "재단에서 제공하는 복리후생 혜택 목록",
    "각 부서별 주요 업무 및 역할",
    "기부금 세금 공제 혜택은 어떻게 받을 수 있나요?",
    "청소년 미디어 교육 프로그램 운영 사례",
    "교육 자료 제작 시 유의할 점",
    "정책 제안서 작성 방법",
    "보고서 작성 시 필수 포함 항목",
    "공공기관과 협업할 때 주의할 점",
    "기록물 보존 기간 및 관리 지침",
    "연구보고서 작성 시 참고할 만한 자료",
    "자원봉사자 관리 및 지원 방안",
    "온라인 교육 플랫폼 활용법",
    "디지털 미디어 활용 가이드",
    "강사 평가 기준 및 피드백 절차",
    "학생 대상 미디어 리터러시 교육 내용",
    "기관별 주요 행사 일정 확인 방법",
    "재단 내부 감사 시 확인해야 할 사항",
    "보호자가 아이에게 스마트폰을 주는 이유?",
    "OOO 강사 전화, 이메일, 소득 구분",
    "강사 평가를 위해 직원이 해야 하는 일?",
    "울산센터, 부산센터의 마을미디어교육 예산을 비교해줘",
    "부산센터 위기 상황 OOO 직원의 역할은?",
    "재단의 CCTV 갯수는?",
    "공문서 작성 시 1,2,3 앞에 띄어쓰기는 몇 칸?",
]
selected_questions = random.sample(example_questions, 10)

# 사이드바
with st.sidebar:
    st.header("질문 예시")
    for question in selected_questions:
        st.write(f"- {question}")
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
