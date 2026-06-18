"""
ai_features.py
TeamMate AI - AI(LLM) 활용 기능

이 프로젝트의 차별화 포인트가 들어 있는 파일입니다.
1) parse_tasks_from_text:
   자연어 문장을 담당자·작업·중요도·완료 여부로 구조화합니다.
2) generate_project_advice:
   현재 프로젝트 상태를 바탕으로 진행 조언을 생성합니다.

OpenAI API 키가 있으면 실제 LLM을 호출하고,
API 키가 없거나 호출에 실패하면 발표 시연을 위해 기본 분석 로직으로 동작합니다.
"""

import json
from typing import Optional

try:
    from openai import OpenAI
    _client = OpenAI()
except Exception:
    _client = None

MODEL = "gpt-4o-mini"


def _strip_code_fence(s: str) -> str:
    """LLM이 ```json ... ``` 형태로 답할 때 코드블록 표시를 제거한다."""
    s = s.strip()
    if s.startswith("```"):
        lines = [ln for ln in s.splitlines() if not ln.strip().startswith("```")]
        s = "\n".join(lines)
    return s.strip()


def _fallback_parse_tasks(text: str, members: Optional[list[str]] = None) -> list[dict]:
    """
    OpenAI API 키가 없을 때 사용하는 기본 자연어 분석 함수.
    문장을 쉼표 단위로 나누고, 담당자와 완료 여부를 간단히 추정한다.
    """
    text = (text or "").strip()
    if not text:
        return []

    parts = (
        text.replace("그리고", ",")
        .replace("하고", ",")
        .replace("했고", ",")
        .replace("고 ", ",")
        .split(",")
    )

    result = []

    for part in parts:
        sentence = part.strip()
        if not sentence:
            continue

        done = any(word in sentence for word in ["완료", "끝냄", "끝냈", "마침", "했다", "했음"])
        importance = "중"

        assignee = None
        if members:
            for m in members:
                if m in sentence:
                    assignee = m
                    break

        task = sentence

        if members:
            for m in members:
                task = task.replace(m, "")

        remove_words = [
            "이", "가", "은", "는", "을", "를",
            "완료", "끝냄", "끝냈고", "끝냈", "마침",
            "했다", "했음", "하는 중", "진행 중", "중",
        ]
        for word in remove_words:
            task = task.replace(word, "")

        task = task.strip()

        if not task:
            task = "작업"

        result.append({
            "assignee": assignee or "미정",
            "task": task,
            "importance": importance,
            "done": done,
        })

    return result


def _fallback_project_advice(project, deadline_days: Optional[int] = None) -> str:
    """
    OpenAI API 키가 없을 때 사용하는 기본 프로젝트 조언 함수.
    진행률, 미완료 작업, 중요도, 작업량을 기준으로 간단한 조언을 만든다.
    """
    progress = project.progress()
    workload = project.workload()

    unfinished = [t for t in project.tasks if not t.done]
    high_priority = [t.name for t in unfinished if t.importance == "상"]

    lines = [f"현재 진행률은 {progress}%입니다."]

    if deadline_days is not None:
        lines.append(f"마감까지 {deadline_days}일 남았습니다.")

    if high_priority:
        lines.append(
            f"중요도 '상' 작업인 {', '.join(high_priority)}부터 먼저 처리하는 것이 좋습니다."
        )
    elif unfinished:
        lines.append(
            f"아직 완료되지 않은 작업이 {len(unfinished)}개 있습니다. 미완료 작업부터 순서대로 확인하세요."
        )
    else:
        lines.append("모든 작업이 완료되었습니다. 최종 검토와 발표 준비를 진행하면 좋습니다.")

    if workload:
        max_member = max(workload, key=workload.get)
        min_member = min(workload, key=workload.get)

        if workload[max_member] - workload[min_member] >= 2:
            lines.append(
                f"{max_member}에게 작업이 몰려 있으므로 {min_member}에게 일부 작업을 재분배하는 것이 좋습니다."
            )
        else:
            lines.append("팀원별 작업량은 비교적 균형 있게 배분되어 있습니다.")

    lines.append("※ 현재 결과는 API 키가 없을 때 제공되는 기본 분석입니다.")

    return "\n\n".join(lines)


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    OpenAI API를 호출하는 함수.
    API 키가 설정되어 있으면 실제 LLM 응답을 반환한다.
    """
    if _client is None:
        raise RuntimeError("OpenAI 클라이언트를 만들 수 없습니다.")

    resp = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def parse_tasks_from_text(text: str, members: Optional[list[str]] = None) -> list[dict]:
    """
    자연어 문장을 작업 목록으로 구조화한다.
    API 호출에 실패하면 기본 분석 함수로 대체한다.
    """
    member_hint = ""
    if members:
        member_hint = (
            f"현재 팀원 목록: {', '.join(members)}. "
            f"별명이나 축약형은 이 목록의 정식 이름으로 맞춰라.\n"
        )

    system_prompt = (
        "너는 조별과제 작업 기록을 구조화하는 도우미다. "
        "사용자 문장에서 각 작업을 뽑아 JSON 배열로만 답한다. "
        "각 원소의 키는 다음과 같다: "
        "assignee(담당자 이름), task(작업명을 간결한 명사형으로), "
        "importance(상/중/하 중 하나, 알 수 없으면 '중'), "
        "done(이미 끝냈으면 true, 진행 중/예정이면 false). "
        "설명·인사말·코드블록·백틱 없이 순수한 JSON 배열만 출력한다."
    )
    user_prompt = member_hint + f"문장: {text}"

    try:
        raw = _strip_code_fence(_call_llm(system_prompt, user_prompt))
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return _fallback_parse_tasks(text, members)


def generate_project_advice(project, deadline_days: Optional[int] = None) -> str:
    """
    현재 프로젝트 상태를 요약해 AI에게 진행 조언을 받는다.
    API 호출에 실패하면 기본 조언 함수로 대체한다.
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
        "2) 지금 먼저 해야 할 작업과 우선순위 "
        "3) 특정 팀원에게 일이 몰렸으면 역할 재분배 제안. "
        "불필요하게 길게 쓰지 말고 핵심만."
    )

    try:
        return _call_llm(system_prompt, state)
    except Exception:
        return _fallback_project_advice(project, deadline_days)