---
name: wb-resume
description: Restores context of a paused task and resumes work from where it was left off. Use when continuing a previously interrupted task in a new session.
metadata:
  author: workbench
  version: "1.5.0"
  skills:
    - vault-conventions
---

# wb-resume: 이어서 작업

중단된 Task의 컨텍스트를 복원하고 이어서 작업합니다.
프론트로딩된 문서만 읽으므로 vault 스캔 없이 빠르게 복원됩니다.

## 입력
- `$ARGUMENTS`: Task 이름 (선택, 없으면 선택)

## 프로세스

### 1. Task 확인

```
$ARGUMENTS가 있으면 해당 Task
없으면:
  - 현재 디렉토리가 data/tasks/{task}/ 내부면 해당 Task
  - 아니면 활성 Task 목록에서 선택
```

### 2. TASK.md 로드

vault TASK.md를 읽어 목표, 서브태스크 상태, 관련 지식을 한번에 복원합니다.
(관련 지식은 wb-start 시 이미 임베딩되어 있음)

```
📋 Task: 결제 기능
🎯 목표: 카드 결제 기능 추가
📋 서브태스크:
✅ 1. PG 연동 (완료, PR #123)
⬜ 2. 결제 UI ← 현재
⬜ 3. 통합 테스트
```

### 3. 현재 SUBTASK.md 로드

```
SUBTASK.md가 없으면:
→ vault-conventions의 최소 템플릿으로 자동 생성
→ "⚠️ SUBTASK.md가 없어서 자동 생성했습니다. /wb-next로 분석을 실행하세요" 안내

SUBTASK.md가 있으면:
→ 분석, 체크리스트, 히스토리가 이미 포함되어 있습니다.
  (wb-next 시 분석 결과가 임베딩됨)
```

### 4. 워크트리 상태 검증

```bash
cd data/tasks/{task}/subtasks/{current}/{repo}/{branch}
git status --porcelain
```

### 5. lastScanned 체크 (경량)

```bash
# TASK.md frontmatter의 lastScanned 타임스탬프로 변경 감지
# lastScanned가 없으면 이 단계 스킵 (하위 호환)
find {vault}/3-Resources -name "*.md" -newer {timestamp_file} | wc -l
```

변경 감지 시:
```
💡 마지막 스캔 이후 {N}개 파일 변경됨.
   /wb-refresh로 관련 지식을 업데이트할 수 있습니다.
```

### 6. 복원 완료 메시지

```
✅ 컨텍스트 복원 완료: 결제 기능

📍 현재 서브태스크: 결제 UI (2/3)

📋 요약:
- 어제 PG 연동 완료
- 오늘은 결제 UI 작업

이어서 작업하세요.
```

## 컨텍스트 복원 순서 (스캔 없음)

```
1. TASK.md (목표 + 서브태스크 + 관련 지식 이미 포함)
2. SUBTASK.md (분석 + 체크리스트 + 히스토리 이미 포함)
3. 워크트리 상태 검증 (dirty 감지)
4. lastScanned 체크 (find -newer, ~0 비용)
```

하지 않는 일:
- ✗ vault 검색 (이미 TASK.md에 임베딩)
- ✗ Archives 검색 (이미 TASK.md에 임베딩)
- ✗ 코드 분석 (이미 SUBTASK.md에 임베딩)

---

## Dirty Worktree 복구

세션이 비정상 종료되면 worktree에 미커밋 변경사항이 남을 수 있습니다.
`wb-resume` 시 자동으로 감지하고 복구 옵션을 제안합니다.

### 미커밋 변경사항 발견 시

```
⚠️ Dirty worktree 감지됨:
   브랜치: feature/{task}/pg-integration
   변경: 3개 파일 (modified 2, untracked 1)

복구 방법:
[1] 변경사항 유지 (이어서 작업)
[2] 임시 커밋 생성
[3] 변경사항 스태시
```

### 워크트리 자체가 없는 경우

```
⚠️ 워크트리가 없습니다.

복구 방법:
[1] 워크트리 재생성 (git worktree add)
[2] 새 브랜치로 시작
```

---

## 활용 내역 표시

```
📊 /wb-resume 실행 완료
├─ 📋 Task: {task-name} ({type})
├─ 📍 서브태스크: {current} ({n}/{total})
├─ ⚠️ Dirty worktree: {복구 여부} (있을 때만)
├─ 💡 Staleness: {N}개 변경 감지 (있을 때만)
└─ ⏱️ 소요: {시간}
```
