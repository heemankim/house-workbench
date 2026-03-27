---
name: wb-pr
description: Creates a pull request for the current subtask with auto-generated description from changes. Use when a subtask implementation is ready for code review.
metadata:
  author: workbench
  version: "2.1.0"
  skills:
    - vault-conventions
---

# wb-pr: PR 생성

현재 서브태스크의 PR을 생성합니다.

## 입력
- `$ARGUMENTS`: 없음

## 프로세스

### 1. 현재 서브태스크 확인

```
서브태스크: PG 연동 (1/3)
레포: backend
브랜치: feature/payment/pg-integration
```

### 2. 변경사항 확인

```
📊 변경사항:
- 커밋: 5개
- 파일: 8개
```

### 3. PR 정보 수집

```
📝 PR 제목:
> feat: PG 연동 (Stripe)

📝 PR 설명 (자동 생성, 수정 가능):
## Summary
- Stripe PG 연동
- Webhook 핸들러 구현

## Related
- Task: 결제 기능
- 서브태스크: PG 연동 (1/3)
```

### 4. PR 생성

```bash
gh pr create --title "..." --body "..." --base develop
```

### 5. vault TASK.md 업데이트

vault 1-Projects/{task}/TASK.md에 PR 번호를 기록합니다.

```markdown
- [x] 01. PG 연동 → PR #123
```

### 6. 완료 메시지

```
✅ PR 생성: #123

🔗 https://github.com/.../pull/123

다음: /wb-next
```

## 여러 레포

```
📦 2개 레포 사용:
- backend: PR #123
- frontend: PR #124
```
