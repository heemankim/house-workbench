---
name: wb-run
description: Executes independent subtasks in parallel using sub-agents. Use when multiple subtasks have no dependencies and can be worked on simultaneously.
metadata:
  author: workbench
  version: "1.5.0"
  skills:
    - vault-conventions
---

# wb-run: 서브태스크 병렬 실행

독립적인 서브태스크들을 병렬로 실행합니다.

## 입력
- `$ARGUMENTS`: Task 이름 (선택, 없으면 현재 Task)

## 전제조건

- `wb-start`로 Task 환경이 세팅되어 있어야 합니다
- 서브태스크별 worktree가 생성되어 있어야 합니다

---

## 프로세스

### 1. Task 상태 확인

TASK.md에서 서브태스크 목록과 상태를 읽습니다:

```
📋 서브태스크 현황:

1. [📦 code] API 엔드포인트 (backend)     → ✅ worktree 준비됨
2. [📦 code] 프론트엔드 UI (frontend)      → ✅ worktree 준비됨
3. [📦 code] 통합 테스트 (backend)         → ⏳ depends: #1, #2
4. [⏳ wait] QA 승인                        → 🚫 실행 불가
```

### 2. 의존성 분석

서브태스크 간 의존성을 확인하고 **지금 실행 가능한 것**만 추립니다:

```
🔍 의존성 분석:

실행 가능 (독립적):
  ✅ #1 API 엔드포인트 — 의존성 없음
  ✅ #2 프론트엔드 UI — 의존성 없음

대기:
  ⏳ #3 통합 테스트 — #1, #2 완료 후
  🚫 #4 QA 승인 — wait 타입 (수동)

2개 서브태스크를 병렬 실행합니다. 진행할까요? (Y/n)
```

### 3. 실행 프롬프트 생성

각 서브태스크용 프롬프트를 자동 생성합니다.
프롬프트에는 다음이 포함됩니다:

```markdown
# 서브태스크 실행 지시

## Task 정보
- Task: {task-name}
- 서브태스크: {subtask-name}
- 유형: {type}

## 목표
{TASK.md에서 해당 서브태스크 설명}

## 컨텍스트
{PLAN.md가 있으면 해당 규칙/매핑 정보}
{CLAUDE.md의 레포 skills 참조}

## 완료 기준
- 코드 구현 완료
- 기존 테스트 통과
- 커밋 생성 (메시지 포함)

## 규칙
- TASK.md의 해당 서브태스크 범위만 작업
- 다른 서브태스크 영역 수정 금지
- 완료 후 결과를 history/에 기록
```

### 4. 병렬 실행

각 서브태스크를 독립적인 headless Claude 세션으로 실행합니다:

```bash
# 서브태스크별 독립 세션 실행
(cd data/tasks/{task}/subtasks/01-api/backend/{branch} && \
  claude -p "{prompt}" \
    --output-format json \
    --allowedTools "Read,Grep,Glob,Edit,Write,Bash" \
    --max-turns 30 \
  > ../../result-01.json 2>&1) &

(cd data/tasks/{task}/subtasks/02-frontend/web/{branch} && \
  claude -p "{prompt}" \
    --output-format json \
    --allowedTools "Read,Grep,Glob,Edit,Write,Bash" \
    --max-turns 30 \
  > ../../result-02.json 2>&1) &
```

### 5. 진행 상황 모니터링

실행 중 상태를 주기적으로 표시합니다:

```
🚀 병렬 실행 중...

  #1 API 엔드포인트    [████████░░] 진행 중  (12 turns)
  #2 프론트엔드 UI     [██████████] 완료     (8 turns)

  경과: 3분 24초
```

### 6. 결과 수합

모든 세션이 완료되면 결과를 정리합니다:

```
┌─────────────────────────────────────────────┐
│ 🏁 병렬 실행 완료                            │
├─────────────────────────────────────────────┤
│                                              │
│ #1 API 엔드포인트     ✅ 성공                │
│    커밋: 3개 (abc1234, def5678, ghi9012)    │
│    변경: 8 files changed                     │
│                                              │
│ #2 프론트엔드 UI      ✅ 성공                │
│    커밋: 2개 (jkl3456, mno7890)             │
│    변경: 5 files changed                     │
│                                              │
├─────────────────────────────────────────────┤
│ 다음 단계:                                   │
│                                              │
│ [1] 결과 리뷰                                │
│     → 각 서브태스크 커밋/변경사항 확인       │
│                                              │
│ [2] 의존성 해소된 서브태스크 실행            │
│     → #3 통합 테스트 (이제 실행 가능)        │
│                                              │
│ [3] /wb-pr --batch로 배치 PR 생성              │
└─────────────────────────────────────────────┘
```

### 6.5. 자동 wb-done 처리

성공한 서브태스크는 자동으로 `wb-done` 상태를 반영합니다:

```
✅ 자동 완료 처리:
  #1 API 엔드포인트 → TASK.md [x] 표시, history 기록
  #2 프론트엔드 UI  → TASK.md [x] 표시, history 기록

SUBTASK.md 가드레일:
  wb-done 0단계에 따라 SUBTASK.md 미존재 시 자동 생성 후 완료 처리

Task 매니저 동기화:
  wb-done 프로시저에 따라 vault 완료 처리
  (local 모드: TASK.md만 업데이트, 외부 어댑터: 해당 어댑터의 절차 수행)
```

> `--no-auto-done` 옵션으로 자동 완료 처리를 비활성화할 수 있습니다.
> 이 경우 각 서브태스크를 수동으로 `/wb-done` 처리해야 합니다.

### 7. 실패 처리

서브태스크가 실패하면:

```
┌─────────────────────────────────────────────┐
│ 🏁 병렬 실행 완료 (1 실패)                  │
├─────────────────────────────────────────────┤
│                                              │
│ #1 API 엔드포인트     ✅ 성공                │
│ #2 프론트엔드 UI      ❌ 실패                │
│    원인: 테스트 실패 (3 failing)             │
│    로그: data/tasks/{task}/subtasks/02/result.json│
│                                              │
├─────────────────────────────────────────────┤
│ 선택:                                        │
│                                              │
│ [1] 실패한 서브태스크만 재실행               │
│ [2] 실패한 서브태스크를 대화형으로 디버깅    │
│     → cd data/tasks/{task}/subtasks/02/... && claude│
│ [3] 성공한 것만 먼저 진행                    │
└─────────────────────────────────────────────┘
```

---

## 실행 옵션

### 기본 실행
```
/wb-run {task-name}
```
→ 독립적인 서브태스크 모두 병렬 실행

### 특정 서브태스크만
```
/wb-run {task-name} --only 1,2
```
→ 지정한 서브태스크만 실행

### 드라이런
```
/wb-run {task-name} --dry-run
```
→ 실제 실행 없이 무엇이 실행될지만 확인

### 모델 지정
```
/wb-run {task-name} --model sonnet
```
→ 서브태스크 실행에 사용할 모델 (기본: sonnet)

### 턴 제한
```
/wb-run {task-name} --max-turns 50
```
→ 각 서브태스크 최대 턴 수 (기본: 30)

### 자동 완료 비활성화
```
/wb-run {task-name} --no-auto-done
```
→ 성공한 서브태스크를 자동 완료 처리하지 않음 (수동 /wb-done 필요)

### 배치 PR 생성
```
/wb-run {task-name} --with-pr
```
→ 모든 서브태스크 성공 시 자동으로 각각 PR 생성
→ 실패한 서브태스크가 있으면 PR 생성 스킵

---

## TASK.md 자동 업데이트

실행 완료 후 TASK.md의 서브태스크 상태를 업데이트합니다:

```markdown
## 서브태스크

1. [📦 code] API 엔드포인트 ✅ 완료 (2026-02-09)
   - 커밋: abc1234, def5678, ghi9012
2. [📦 code] 프론트엔드 UI ✅ 완료 (2026-02-09)
   - 커밋: jkl3456, mno7890
3. [📦 code] 통합 테스트 → 실행 가능 (의존성 해소)
4. [⏳ wait] QA 승인 → 대기 중
```

---

## history/ 기록

각 서브태스크 세션의 결과를 히스토리에 기록합니다:

```markdown
### 2026-02-09: wb-run 병렬 실행

**실행된 서브태스크:**
- #1 API 엔드포인트: ✅ 성공 (8 turns, 2분 12초)
- #2 프론트엔드 UI: ✅ 성공 (12 turns, 3분 45초)

**총 소요:** 3분 45초 (병렬)
**순차 대비 절감:** 2분 12초
```

---

## 활용 내역 표시

```
📊 /wb-run 실행 완료
├─ 🤖 Sessions: 2개 (headless, sonnet)
├─ ⏱️ 소요: 3분 45초 (순차 시 5분 57초)
├─ 📦 커밋: 5개 생성
├─ 📝 결과:
│   ├─ #1 API 엔드포인트: ✅
│   └─ #2 프론트엔드 UI: ✅
└─ 📋 다음: #3 통합 테스트 (unblocked)
```
