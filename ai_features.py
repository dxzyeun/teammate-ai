"""
ai_features.py
TeamMate AI - AI(LLM) 활용 기능

이 프로젝트의 '차별화 포인트'가 들어 있는 파일입니다.
  1) parse_tasks_from_text  : 자연어 문장 -> 작업 목록(구조화)
       예) "다은이가 설문 20문항 만들고 철수가 코드 리뷰함"
           -> [{"assignee":"이다은","task":"설문 문항 작성","importance":"중","done":true}, ...]
  2) generate_project_advice: 현재 프로젝트 상태 -> 진행 조언 생성

[중요] LLM 호출은 _call_llm() 한 곳에만 모아 두었습니다.
       OpenAI -> Claude(Anthropic) 등으로 바꾸고 싶으면 그 함수만 고치면 됩니다.

준비물:
  pip install openai
  환경변수에 API 키 설정 (예: 터미널에서  export OPENAI_API_KEY="sk-..." )
"""

import json
import os
from typing import Optional

# OpenAI SDK 준비. 키가 없거나 미설치여도 import 자체는 실패하지 않게 처리.
try:
    from openai import OpenAI
    _client = OpenAI()  # OPENAI_API_KEY 환경변수를 자동으로 읽음
except Exception:
    _client = None

MODEL = "gpt-4o-mini"   # 저렴하고 빠른 모델. 필요하면 바꿔도 됨.


def _strip_code_fence(s: str) -> str:
    """LLM이 ```json ... ``` 처럼 감싸서 줄 때 백틱 줄을 제거한다."""
    s = s.strip()
    if s.startswith("```"):
        lines = [ln for ln in s.splitlines() if not ln.strip().startswith("```")]
        s = "\n".join(lines)
    return s.strip()


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    LLM 호출을 한 곳에 모아 둔 함수.
    >>> 공급자(OpenAI/Claude 등)를 바꾸려면 이 함수 내부만 수정하면 됩니다.
    """
    if _client is None:
        raise RuntimeError(
            "OpenAI 클라이언트를 만들 수 없습니다. "
            "`pip install openai` 후 OPENAI_API_KEY 환경변수를 설정하세요."
        )
    resp = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,   # 낮을수록 일관된(덜 창의적인) 답
    )
    return resp.choices[0].message.content.strip()


def parse_tasks_from_text(text: str,
                          members: Optional[list[str]] = None) -> list[dict]:
    """
    자연어 한 문장(또는 여러 문장)을 작업 목록으로 구조화한다.
    규칙 기반으로는 불가능하고 AI가 있어야만 돌아가는 핵심 기능.

    반환 예:
      [{"assignee": "이다은", "task": "발표 대본 작성",
        "importance": "중", "done": true}, ...]
    """
    member_hint = ""
    if members:
        member_hint = (
            f"현재 팀원 목록: {', '.join(members)}. "
            f"별명/축약형(예: '다은이')은 이 목록의 정식 이름으로 맞춰라.\n"
        )

    system_prompt = (
        "너는 조별과제 작업 기록을 구조화하는 도우미다. "
        "사용자 문장에서 각 작업을 뽑아 JSON 배열로만 답한다. "
        "각 원소의 키는 다음과 같다: "
        "assignee(담당자 이름), task(작업명을 간결한 명사형으로), "
        "importance(상/중/하 중 하나, 알 수 없으면 '중'), "
        "done(이미 끝냈으면 true, 진행 중/예정이면 false). "
        "설명·인사말·코드블록·백틱 없이 '순수한 JSON 배열'만 출력한다."
    )
    user_prompt = member_hint + f"문장: {text}"

    raw = _strip_code_fence(_call_llm(system_prompt, user_prompt))
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        # 혹시 형식이 깨져도 프로그램이 죽지 않도록 빈 목록 반환
        return []


def generate_project_advice(project, deadline_days: Optional[int] = None) -> str:
    """
    현재 프로젝트 상태를 요약해 AI에게 진행 조언을 받는다.
    project: models.Project 객체
    """
    state_lines = [project.summary_text(), "", "작업 목록:"]
    for t in project.tasks:
        status = "완료" if t.done else "미완료"
        who = t.assignee or "미정"
        state_lines.append(f"- {t.name} (담당:{who}, 중요도:{t.importance}, {status})")
    if deadline_days is not None:
        state_lines.append(f"\n마감까지 남은 일수: {deadline_days}일")
    state = "\n".join(state_lines)

    system_prompt = (
        "너는 대학생 조별과제 팀의 진행을 돕는 조언자다. "
        "주어진 프로젝트 상태를 보고 한국어로 다음 세 가지를 간결하게 제시하라. "
        "1) 현재 상황 한 줄 요약 "
        "2) 지금 먼저 해야 할 작업(우선순위) "
        "3) 특정 팀원에게 일이 몰렸으면 역할 재분배 제안. "
        "불필요하게 길게 쓰지 말고 핵심만."
    )
    return _call_llm(system_prompt, state)
