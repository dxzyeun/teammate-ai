"""
models.py
TeamMate AI - 핵심 데이터 모델과 계산 로직

이 파일에는 화면(UI) 코드가 전혀 없습니다.
팀원/작업 데이터를 다루고 진행률·기여도를 계산하는 '두뇌'만 들어 있어요.
이렇게 UI와 분리해 두면 단독으로 테스트할 수 있고, 나중에
스트림릿(Streamlit) 화면을 입히기도 쉽습니다.
"""

from dataclasses import dataclass, field
from typing import Optional


# 작업 중요도 -> 가중치. 숫자가 클수록 중요한 작업으로 본다.
IMPORTANCE_WEIGHT = {"상": 3, "중": 2, "하": 1}


@dataclass
class Task:
    """하나의 작업(할 일)을 표현한다."""
    name: str
    assignee: Optional[str] = None   # 담당자 이름 (아직 미정이면 None)
    importance: str = "중"            # "상" / "중" / "하"
    done: bool = False                # 완료했으면 True

    @property
    def weight(self) -> int:
        """중요도 글자를 점수(가중치)로 바꿔 준다."""
        return IMPORTANCE_WEIGHT.get(self.importance, 2)


@dataclass
class Project:
    """프로젝트 하나 = 팀원 목록 + 작업 목록 + 계산 기능."""
    name: str
    members: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    # ----- 팀원 관리 -----
    def add_member(self, name: str) -> None:
        """팀원을 추가한다. 빈 이름이나 중복은 무시."""
        name = (name or "").strip()
        if name and name not in self.members:
            self.members.append(name)

    # ----- 작업 관리 -----
    def add_task(self, name: str, assignee: Optional[str] = None,
                 importance: str = "중", done: bool = False) -> Task:
        """작업을 추가한다. 담당자가 새 이름이면 팀원에도 자동 등록."""
        task = Task(name=name.strip(), assignee=assignee,
                    importance=importance, done=done)
        self.tasks.append(task)
        if assignee:
            self.add_member(assignee)
        return task

    def complete_task(self, task_name: str) -> bool:
        """작업명을 받아 완료 처리한다. 찾으면 True."""
        for t in self.tasks:
            if t.name == task_name:
                t.done = True
                return True
        return False

    # ----- 진행률 -----
    def progress(self) -> float:
        """전체 작업 중 완료된 비율(%)."""
        if not self.tasks:
            return 0.0
        done = sum(1 for t in self.tasks if t.done)
        return round(done / len(self.tasks) * 100, 1)

    # ----- 기여도 -----
    def contribution_scores(self) -> dict[str, float]:
        """
        팀원별 기여도(%)를 계산한다.
        '완료한 작업'의 중요도 가중치를 더해 점수를 내고,
        전체 합이 100%가 되도록 비율로 환산한다.
        (아직 안 끝낸 작업은 점수에 안 들어감 -> '실제로 한 일' 기준)
        """
        raw = {m: 0 for m in self.members}
        for t in self.tasks:
            if t.done and t.assignee in raw:
                raw[t.assignee] += t.weight
        total = sum(raw.values())
        if total == 0:
            return {m: 0.0 for m in self.members}
        return {m: round(score / total * 100, 1) for m, score in raw.items()}

    # ----- 작업량 쏠림 분석 (AI 조언의 재료) -----
    def workload(self) -> dict[str, int]:
        """팀원별로 '맡은 작업 개수'를 센다."""
        load = {m: 0 for m in self.members}
        for t in self.tasks:
            if t.assignee in load:
                load[t.assignee] += 1
        return load

    # ----- 요약 (README/조언용 텍스트) -----
    def summary_text(self) -> str:
        """현재 상태를 사람이 읽기 좋은 글로 정리한다."""
        done = sum(1 for t in self.tasks if t.done)
        lines = [
            f"프로젝트명: {self.name}",
            f"진행률: {self.progress()}% ({done}/{len(self.tasks)} 완료)",
            f"팀원별 작업 개수: {self.workload()}",
            f"팀원별 기여도(%): {self.contribution_scores()}",
        ]
        return "\n".join(lines)
