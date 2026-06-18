"""
app.py  [이다은(본인) 담당 — 메인 흐름/통합 + 자연어 입력]

전체 화면을 조립하는 메인 파일입니다.
실행:  streamlit run app.py

[담당 구분]
  - 이다은(본인): 이 파일(전체 틀, 팀원 등록, 자연어 입력), models.py, ai_features.py
  - 양서윤: sections.py (작업 관리 + 대시보드 지표)
  - 윤재웅: charts.py (기여도 그래프), advice.py (AI 조언 화면)
"""

import streamlit as st

from models import Project
from ai_features import parse_tasks_from_text
from sections import render_task_section, render_dashboard   # 양서윤
from charts import render_contribution_chart                  # 윤재웅
from advice import render_advice_section                       # 윤재웅


# ---------- 기본 설정 ----------
st.set_page_config(page_title="AI 조별과제 매니저", page_icon="🤝", layout="wide")

if "project" not in st.session_state:
    st.session_state.project = Project(name="AI 조별과제 매니저")
project = st.session_state.project

st.title("🤝 AI 조별과제 매니저")
st.caption("팀 프로젝트의 역할·진행률·기여도를 한눈에 관리하세요.")


# ---------- 사이드바: 팀원 등록 (이다은) ----------
with st.sidebar:
    st.header("👥 팀원 관리")

    st.subheader("📈 프로젝트 현황")

    st.metric("현재 진행률", f"{project.progress()}%")
    st.metric("전체 작업 수", len(project.tasks))
    st.metric("팀원 수", len(project.members))

    st.divider()
    
    new_member = st.text_input("팀원 이름 입력")
    if st.button("팀원 추가", width="stretch"):
        if new_member.strip():
            project.add_member(new_member)
            st.success(f"'{new_member.strip()}' 추가됨")
        else:
            st.warning("이름을 입력하세요.")

    st.write("**현재 팀원**")
    if project.members:
        for m in project.members:
            st.write(f"- {m}")
    else:
        st.write("_(아직 없음)_")


# ---------- 메인: 탭 ----------
tab_task, tab_dash, tab_nl, tab_advice = st.tabs(
    ["📋 작업 관리", "📊 대시보드", "💬 자연어 입력", "🤖 AI 조언"]
)

# 탭1: 작업 관리 — 양서윤 (sections.py)
with tab_task:
    render_task_section(project)

# 탭2: 대시보드 — 양서윤(지표) + 윤재웅(기여도 그래프)
with tab_dash:
    render_dashboard(project)            # 양서윤
    st.divider()
    render_contribution_chart(project)   # 윤재웅

# 탭3: 자연어 입력 — 이다은 (완성). 이 프로젝트의 차별화 기능.
with tab_nl:
    st.subheader("자연어로 작업 기록하기")
    st.write("문장을 그대로 적으면 AI가 담당자·작업·완료여부로 정리해 등록합니다.")
    st.caption("예: \"다은이가 발표 대본 끝냈고 영희가 데이터 분석 중\"")
    text = st.text_area("작업 내용을 문장으로 입력", height=100)
    if st.button("AI로 분석해서 추가"):
        if not text.strip():
            st.warning("문장을 입력하세요.")
        else:
            try:
                with st.spinner("AI가 문장을 분석하는 중..."):
                    parsed = parse_tasks_from_text(text, members=project.members)
                if not parsed:
                    st.warning("작업을 추출하지 못했어요. 문장을 더 구체적으로 써보세요.")
                else:
                    for item in parsed:
                        name = item.get("task", "이름없음")
                        done = item.get("done", False)
                        if done and project.complete_task(name):
                            continue
                        project.add_task(name, assignee=item.get("assignee"),
                                         importance=item.get("importance", "중"), done=done)
                    st.success("AI가 정리한 결과를 등록했습니다.")
                    st.json(parsed)
            except Exception as e:
                st.error(f"AI 호출에 실패했습니다: {e}")

# 탭4: AI 조언 — 윤재웅 (advice.py)
with tab_advice:
    render_advice_section(project)
