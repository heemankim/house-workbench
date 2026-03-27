---
name: wb-save
description: Saves current work progress including history, decisions, and task state. Use when pausing work to preserve context for later resumption.
metadata:
  author: workbench
  version: "2.1.0"
  skills:
    - vault-conventions
---

# wb-save: 중간 저장

현재 작업 상태를 저장합니다.

## 입력
- `$ARGUMENTS`: 저장 메모 (선택)

## 프로세스

### 1. 현재 Task 확인

`data/tasks/{task-name}/` 내부여야 함

### 2. 히스토리 업데이트

> 히스토리는 data/tasks/ history/ 에 기록합니다 (작업 파일).
> 의사결정은 vault decisions.md 에 기록합니다 (SSoT).

`history/YYYY-MM-DD.md`에 기록:

```markdown
### 중간 저장 - HH:MM

#### 진행 상황
- 현재 서브태스크: 결제 UI (2/3)
- 변경된 파일: 5개

#### 메모
{$ARGUMENTS 또는 사용자 입력}

#### 미커밋 변경사항
- frontend/src/Payment.tsx (modified)
- frontend/src/api/payment.ts (new)
```

### 3. 의사결정 감지

```
💡 의사결정이 감지되었습니다:
"결제 UI는 모달 대신 페이지로 구현"

→ vault decisions.md에 저장합니다.
```

### 4. 완료 메시지

```
✅ 저장 완료

📅 저장 시간: 2024-02-06 14:30
📋 서브태스크: 결제 UI (2/3)

/wb-resume으로 이어서 작업할 수 있습니다.
```
