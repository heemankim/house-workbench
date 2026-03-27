---
name: branch-rules
description: Defines branch naming conventions for workspaces. Use when creating branches for tasks and subtasks.
metadata:
  author: workbench
  version: "1.5.0"
---

# branch-rules: 브랜치 네이밍 규칙

기본 브랜치 네이밍 규칙입니다. Workspace에서 오버라이드 가능합니다.

## 기본 패턴

```
feature/{task}/{subtask}
```

- 스타일: kebab-case (영문 소문자, 하이픈 구분)
- baseBranch: config.json의 `defaults.baseBranch` 참조

## 사용 가능한 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `{task}` | Task 이름 | `payment-v2` |
| `{subtask}` | 서브태스크 이름 | `pg-integration` |
| `{index}` | 서브태스크 번호 | `01` |
| `{type}` | 커밋 타입 (`feature`, `fix`, `chore`) | `feature` |
| `{ticket}` | 외부 티켓 ID | `HOUSE-1234` |
| `{date}` | 날짜 (YYYYMMDD) | `20260209` |

## 예시

```
Task: payment-v2, 서브태스크: pg-integration
→ feature/payment-v2/pg-integration
```

## Workspace 오버라이드

Workspace `.claude/skills/`에 같은 주제의 skill을 두면 이 기본 규칙 대신 적용됩니다.
