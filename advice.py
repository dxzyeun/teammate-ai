"""
advice.py  [윤재웅 담당 ② — AI 조언 화면]

▶ render_advice_section(project) 를 완성하세요.
  - st.number_input 으로 '마감까지 남은 일수'를 받고
  - st.button("조언 받기") 를 누르면 generate_project_advice(project, deadline_days=...) 호출
  - 결과를 st.write 로 표시 (작업이 없으면 안내, 오류는 try/except 로 처리)

[쓸 수 있는 함수] (ai_features.py 에 이미 구현됨)
  from ai_features import generate_project_advice
  generate_project_advice(project, deadline_days=정수)  -> 조언 텍스트
"""

import streamlit as st
from ai_features import generate_project_advice


def render_advice_section(project):
    st.subheader("AI 프로젝트 조언")
    # TODO(윤재웅-2): 마감 일수 입력 → '조언 받기' 버튼 → generate_project_advice 호출 → 결과 표시
    st.info("🤖 [윤재웅] AI 조언 화면을 구현하세요.")
