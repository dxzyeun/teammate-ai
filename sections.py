"""
sections.py  [양서윤 담당 — 작업 관리 + 대시보드 지표]

▶ 함수 2개를 완성하세요. (각각 따로 커밋하면 좋아요)
  1) render_task_section(project) : 작업 등록·완료·목록
  2) render_dashboard(project)    : 진행률·완료·전체 지표

[쓸 수 있는 함수] (models.py 에 이미 구현됨)
  project.add_task(이름, assignee=담당자, importance="상"/"중"/"하")
  project.tasks / project.members / project.progress()

[위젯 힌트] st.text_input · st.selectbox · st.button · st.checkbox · st.metric · st.columns · st.progress
"""

import streamlit as st


def render_task_section(project):
    st.subheader("작업 관리")
    # TODO(양서윤-1): 작업 등록 폼 (작업명/담당자/중요도 + 추가 버튼)
    # TODO(양서윤-2): 작업 목록 + 완료 체크박스
    st.info("⛏️ [양서윤] 작업 관리 화면을 구현하세요.")


def render_dashboard(project):
    # TODO(양서윤-3): 진행률·완료·전체 지표(st.metric) + 진행률 막대(st.progress)
    st.info("⛏️ [양서윤] 대시보드 지표를 구현하세요.")
