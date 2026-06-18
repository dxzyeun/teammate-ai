"""
sections.py  [양서윤 담당 — 작업 관리 화면]
작업 등록 · 완료 처리 · 진행률 표시를 담당합니다.
"""

import streamlit as st


def render_task_section(project):
    st.subheader("작업 관리")

    # 새 작업 등록 폼
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        task_name = st.text_input("작업명", key="new_task_name")
    with col2:
        assignee = st.selectbox("담당자", options=["(미정)"] + project.members,
                                key="new_task_assignee")
    with col3:
        importance = st.selectbox("중요도", options=["상", "중", "하"],
                                  index=1, key="new_task_importance")

    if st.button("작업 추가"):
        if task_name.strip():
            who = None if assignee == "(미정)" else assignee
            project.add_task(task_name, assignee=who, importance=importance)
            st.success(f"'{task_name.strip()}' 추가됨")
            st.rerun()
        else:
            st.warning("작업명을 입력하세요.")

    st.divider()

    # 작업 목록 + 완료 체크
    if not project.tasks:
        st.write("아직 등록된 작업이 없습니다.")
    else:
        for i, t in enumerate(project.tasks):
            label = f"{t.name}  ·  담당: {t.assignee or '미정'}  ·  중요도: {t.importance}"
            t.done = st.checkbox(label, value=t.done, key=f"task_done_{i}")

    st.divider()

    # 진행률 표시
    st.metric("진행률", f"{project.progress()}%")
    st.progress(project.progress() / 100)