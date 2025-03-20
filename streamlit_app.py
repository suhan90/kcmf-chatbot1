import streamlit as st
import requests
import os

# API 엔드포인트 (App Engine 또는 Cloud Run에 배포된 주소)
API_URL = os.environ.get("API_URL")
# 허용된 IP 목록, 암호
ALLOWED_IPS = os.environ.get("API_URL")
ACCESS_PASSWORD = os.environ.get("ACCESS_PASSWORD")

st.set_page_config(
    page_title="KCMF 문서 Q&A 챗봇",
    page_icon="📚",
    layout="wide"
)

st.title("KCMF 문서 Q&A 챗봇(v0.3)")

# 사용자 IP 확인 함수
# JavaScript를 사용하여 클라이언트 IP 가져오기
st.markdown(
    """
    <script>
        async function getIP() {
            let response = await fetch('https://api64.ipify.org?format=json');
            let data = await response.json();
            let queryParams = new URLSearchParams(window.location.search);
            queryParams.set("client_ip", data.ip);
            window.location.search = queryParams.toString();
        }
        if (!new URLSearchParams(window.location.search).has("client_ip")) {
            getIP();
        }
    </script>
    """,
    unsafe_allow_html=True,
)
# Streamlit에서 URL 파라미터로 받은 IP 확인
query_params = st.query_params
client_ip = query_params.get("client_ip", "알 수 없음")
st.write(f"당신의 IP: {client_ip}")

# IP 검사 및 암호 인증 확인
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if client_ip not in ALLOWED_IPS:
    st.warning(f"현재 IP: {client_ip} (허용되지 않은 IP입니다.)")
    password = st.text_input("암호를 입력하세요:", type="password")
    if st.button("확인"):
        if password == ACCESS_PASSWORD:
            st.session_state.authenticated = True
            st.success("인증 성공!")
        else:
            st.error("잘못된 암호입니다.")
if client_ip not in ALLOWED_IPS and not st.session_state.authenticated:
    st.stop()
    

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바
with st.sidebar:
    st.header("안내")
    st.write("""
    #### 제공된 자료:\n
    - 재단 규정, 규칙, 지침\n
    - 업무 절차서, 매뉴얼\n
    - 미디어교육 연구보고서, 교재\n
    \n
    #### 필요한 자료:\n
    - 방송시설,장비 매뉴얼\n
    - 업무 관련 FAQ, Q&A\n
    \n
    #### 주의사항:\n
    - 답변은 검색 결과에 바탕하며, 논리적 오류와 허점이 있을 수 있습니다. 참고로만 쓰시고, 필요한 경우 근거를 확인하세요.\n
    - 사용량이 많을 경우 요금이 부과됩니다.\n
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
