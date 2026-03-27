---
name: wb
description: Displays Workbench framework help and current workspace status. Use when needing an overview of available commands or workspace state.
metadata:
  author: workbench
  version: "1.5.0"
---

# wb: Workbench 헬퍼

Workbench 프레임워크 도움말 및 상태를 표시합니다.

## 입력
- `$ARGUMENTS`: 도움말 주제 (선택)

## 프로세스

### 인자 없이 실행 시

현재 상태와 사용 가능한 명령어를 표시:

```
🛠️ Workbench

📍 현재 위치: {workspace 또는 task 경로}

📋 명령어:
  /wb-start        Task 시작
  /wb-resume       이어서 작업
  /wb-save         중간 저장
  /wb-done         서브태스크 완료
  /wb-next         다음 서브태스크
  /wb-end          Task 종료
  /wb-status       상태 조회
  /wb-add-subtask  서브태스크 추가
  /wb-save-skill   Skill로 저장
  /wb-pr           PR 생성
  /wb-update       Workspace 업데이트

💡 /wb {주제} 로 상세 도움말
   예: /wb start, /wb skills
```

### 주제별 도움말

`/wb start` → /wb-start 명령어 상세 설명
`/wb skills` → Skills 시스템 설명
`/wb agents` → Agents 사용법
`/wb hooks` → Hooks 설명

### 현재 상태 감지

1. `data/tasks/{task-name}/` 내부:
   - 현재 Task 이름, 서브태스크 상태 표시

2. Workspace 루트:
   - 활성 Task 목록 표시

3. 그 외:
   - 기본 도움말만 표시
