---
name: wb-add-subtask
description: Adds a new subtask to the current task with proper ordering and numbering. Use when discovering additional work items during task execution.
metadata:
  author: workbench
  version: "2.1.0"
  skills:
    - vault-conventions
---

# wb-add-subtask: 서브태스크 추가

작업 중 새로운 서브태스크를 추가합니다.

## 입력
- `$ARGUMENTS`: 서브태스크 이름

## 프로세스

> ⚠️ **Vault-First**: vault 1-Projects/{task}/ 가 SSoT입니다.
> vault TASK.md → vault SUBTASK.md → data/tasks/ 포인터 순서로 생성합니다.

### 1. 서브태스크 이름 확인

```
📝 추가할 서브태스크 이름:
> 에러 핸들링
```

### 2. 순서 결정

```
현재:
1. [완료] PG 연동
2. [진행중] 결제 UI
3. [대기] 통합 테스트

어디에 추가? (기본: 마지막)
```

### 3. Vault TASK.md 체크리스트 업데이트 (SSoT)

vault 1-Projects/{task}/TASK.md 의 서브태스크 체크리스트에 새 항목을 추가합니다.

```markdown
## 서브태스크
- [x] 01. PG 연동
- [ ] 02. 결제 UI
- [ ] 03. 에러 핸들링 ← 추가
- [ ] 04. 통합 테스트
```

### 4. Vault subtasks/ 에 SUBTASK.md 생성

vault-conventions의 "SUBTASK.md 최소 템플릿"으로 vault 내 SUBTASK.md를 생성합니다.
디렉토리만 있고 SUBTASK.md가 없는 상태는 허용하지 않습니다.

```
1-Projects/{task}/subtasks/03-error-handling/
└── SUBTASK.md    # status: pending, subtask_type: {사용자 선택 또는 Task 기본 유형}
```

### 5. data/tasks/ 미러링

vault에서 생성한 내용을 data/tasks/ 에 포인터로 미러링합니다.

```
data/tasks/{task}/subtasks/03-error-handling/
└── SUBTASK.md
```

### 6. 완료 메시지

```
✅ 서브태스크 추가: 에러 핸들링

/wb-next 3으로 바로 시작 가능
```
