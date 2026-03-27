---
name: wb-status
description: Displays workspace and task status including subtask progress, active branches, and pending PRs. Use when checking overall project state.
metadata:
  author: workbench
  version: "2.1.0"
  skills:
    - vault-conventions
---

# wb-status: 상태 조회

현재 Workspace와 Task들의 상태를 조회합니다.

## 입력
- `$ARGUMENTS`: Task 이름 (선택)

## 데이터 소스

> **Vault가 SSoT** — config.json의 `vault` 필드 경로 기준:
> - 활성 태스크: `{vault}/1-Projects/*/TASK.md` 스캔
> - 완료 태스크: `{vault}/4-Archives/*/`
> - `data/tasks/` 디렉토리가 아닌 **vault의 1-Projects/**를 반드시 읽을 것

## 프로세스

### 인자 없이 (Workspace 전체)

1. `config.json`에서 `vault` 경로 확인
2. `{vault}/1-Projects/*/TASK.md`를 모두 읽어 활성 태스크 목록 구성
3. 각 TASK.md의 서브태스크 체크리스트에서 완료/전체 수 파싱
4. `{vault}/1-Projects/{task}/subtasks/*/SUBTASK.md`에서 status 필드 확인
5. TASK.md의 TL;DR 또는 목표에서 1줄 요약 포함

```
📊 Workspace: {name}

📋 활성 Task:
┌─────────────────┬───────────────┬─────────────┬─────────────────────┐
│ Task            │ 서브태스크     │ 상태        │ 설명                │
├─────────────────┼───────────────┼─────────────┼─────────────────────┤
│ 결제 기능        │ 2/3 완료      │ 진행중      │ PG 연동 + 결제 UI   │
│ 로그인 버그      │ 1/1 완료      │ PR 대기     │ OAuth 토큰 갱신 수정│
└─────────────────┴───────────────┴─────────────┴─────────────────────┘

💡 /wb-status {task}로 상세 조회
```

### Task 지정 시

1. `{vault}/1-Projects/{task}/TASK.md` 읽기
2. 서브태스크 체크리스트 파싱 (상태 아이콘: ✅⏳🚫⬜)
3. `subtasks/*/SUBTASK.md` frontmatter에서 repo, branch, status 확인
4. 관련 PR이 있으면 `gh pr list`로 상태 조회

```
📊 Task: 결제 기능

📋 서브태스크:
┌────┬─────────────┬────────────┬─────────┐
│ #  │ 이름        │ 레포       │ 상태    │
├────┼─────────────┼────────────┼─────────┤
│ 1  │ PG 연동     │ backend    │ ✅ 완료 │
│ 2  │ 결제 UI     │ frontend   │ 🔄 진행 │
│ 3  │ 통합 테스트  │ both       │ ⬜ 대기 │
└────┴─────────────┴────────────┴─────────┘

🔗 PR:
- #123: PG 연동 (merged)
- #124: 결제 UI (draft)
```
