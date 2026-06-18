"""
advice.py  [윤재웅 담당 ② — AI 조언 화면]

마감까지 남은 일수를 입력받고,
AI가 현재 프로젝트 상황을 분석해 조언을 제공하는 화면입니다.
"""

import streamlit as st
from ai_features import generate_project_advice


def render_advice_section(project):
    st.subheader("AI 프로젝트 조언")

    # 작업이 하나도 없을 때 안내
    if not project.tasks:
        st.info("등록된 작업이 있어야 AI 조언을 받을 수 있습니다.")
        return

    # 마감까지 남은 일수 입력
    deadline_days = st.number_input(
        "마감까지 남은 일수",
        min_value=0,
        value=7,
        step=1,
    )

    # 버튼을 눌렀을 때 AI 조언 생성
    if st.button("조언 받기"):
        try:
            advice = generate_project_advice(
                project,
                deadline_days=int(deadline_days),
            )
            st.write(advice)

        except Exception:
            st.warning("API 키가 없어 기본 조언을 표시합니다.")

            progress = project.progress()
            workload = project.workload()

            advice = f"""
현재 진행률은 {progress}%입니다.

우선 아직 완료되지 않은 작업부터 확인하고,
중요도 '상'인 작업을 먼저 끝내는 것이 좋습니다.

팀원별 작업 수는 {workload} 입니다.
특정 팀원에게 작업이 몰려 있다면 역할을 다시 나누는 것이 좋습니다.
"""
            st.write(advice)