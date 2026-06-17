"""
charts.py  [윤재웅 담당 ① — 기여도 그래프 시각화]

▶ render_contribution_chart(project) 를 완성하세요.
  - project.contribution_scores() 로 팀원별 기여도(%) 딕셔너리를 얻고
  - px.bar(막대) / px.pie(원) 로 그려 st.plotly_chart(...) 로 표시

[힌트]
  import plotly.express as px
  names = list(scores.keys()); values = list(scores.values())
"""

import streamlit as st


def render_contribution_chart(project):
    st.subheader("팀원별 기여도")
    scores = project.contribution_scores()
    # TODO(윤재웅-1): scores 를 막대그래프 + 원그래프로 시각화
    st.info("📊 [윤재웅] 기여도 그래프를 구현하세요.")
    st.write("참고용 데이터:", scores)  # 구현 후 지워도 됨
