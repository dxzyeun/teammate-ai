"""
charts.py  [윤재웅 담당 — 기여도 그래프 시각화]
팀원별 기여도를 막대그래프와 원그래프로 보여줍니다.
"""

import streamlit as st
import plotly.express as px


def render_contribution_chart(project):
    st.subheader("팀원별 기여도")

    scores = project.contribution_scores()

    if not scores or sum(scores.values()) == 0:
        st.info("완료된 작업이 있어야 기여도가 계산됩니다.")
        return

    names = list(scores.keys())
    values = list(scores.values())

    col1, col2 = st.columns(2)

    with col1:
        fig_bar = px.bar(
            x=names,
            y=values,
            labels={"x": "팀원", "y": "기여도(%)"},
            title="기여도 (막대그래프)",
        )
        st.plotly_chart(fig_bar, width="stretch")

    with col2:
        fig_pie = px.pie(
            names=names,
            values=values,
            title="기여도 (원그래프)",
        )
        st.plotly_chart(fig_pie, width="stretch")
