---
name: wb-next
description: Advances to the next subtask by creating a worktree and running deep analysis. Use when the current subtask is complete and the next one needs to start.
metadata:
  author: workbench
  version: "2.1.0"
  skills:
    - vault-conventions
---

# wb-next: 다음 서브태스크

다음 서브태스크로 이동하고 워크트리를 생성합니다.

## 입력
- `$ARGUMENTS`: 서브태스크 번호 (선택)

## 프로세스

### 1. 현재 상태 확인

```
현재: PG 연동 (1/3) - 완료
다음: 결제 UI (2/3)
```

미완료면 경고:
```
⚠️ 현재 서브태스크가 완료되지 않았습니다.
/wb-done으로 먼저 완료하거나, 강제로 넘어가시겠습니까?
```

### 2. 다음 서브태스크 선택

```
/wb-next 3  → 3번으로 이동
```

### 3. 레포/브랜치 결정

```
📦 "결제 UI" 서브태스크
예상 레포: frontend
브랜치: feature/{task-name}/payment-ui
```

### 4. 워크트리 생성

```bash
cd repos/{repo-name}
git fetch origin
git pull origin {defaultBase}
git worktree add ../../data/tasks/{task-name}/subtasks/{nn}-xxx/{repo}/{branch} -b {branch}
```

> `{defaultBase}`는 repos.json의 `defaultBase` 값 (기본: main).
> pull로 로컬 base 브랜치를 최신 상태로 만든 후 worktree를 생성합니다.

### 4.5. SUBTASK.md 존재 확인

```
SUBTASK.md가 없으면:
→ vault subtasks/{nn}/ 에 먼저 생성
→ data/tasks/ subtasks/{nn}/ 에 미러링
→ vault-conventions의 최소 템플릿으로 자동 생성
→ "⚠️ SUBTASK.md가 없어서 자동 생성했습니다" 안내

SUBTASK.md가 있으면:
→ vault SUBTASK.md를 SSoT로 읽음
→ 정상 진행 (subtask-analyzer가 분석 섹션을 채움)
```

### 5. 서브태스크 분석 (subtask-analyzer)

`subtask-analyzer`를 실행하여 SUBTASK.md에 분석 결과를 임베딩합니다:
- 영향 범위, 작업 체크리스트, 리스크
- Vault 관련 지식 검색 결과도 SUBTASK.md `## 관련 지식`에 임베딩

```
config.json `beta.fts-indexer` 확인:

FTS5 모드 (true):
  python3 tools/vault-search.py search "{query}" --vault {vault} --limit 10
  → JSON 결과에서 path, title, tldr 추출

grep 모드 (false/미설정):
  Stage 1: frontmatter tags grep
  Stage 2: TL;DR 섹션 grep

SUBTASK.md에 기록:
## 관련 지식
- [[responsive-design-guide]] — 모바일 반응형 가이드
- [[payment-ui-pattern]] — 결제 UI 패턴

TASK.md lastScanned 타임스탬프 갱신
```

이후 wb-resume 시 SUBTASK.md만 읽으면 관련 지식이 이미 포함되어 있습니다.

### 6. 완료 메시지

```
✅ 서브태스크 시작: 결제 UI (2/3)

📁 경로: data/tasks/{task}/subtasks/02-payment-ui/
🌿 브랜치: feature/{task-name}/payment-ui
📚 관련 지식: 2건 (SUBTASK.md에 임베딩됨)

/wb-done으로 완료
```

## 같은 레포, 다른 브랜치

```
⚠️ frontend 레포는 이전 서브태스크에서도 사용.
새 브랜치로 분리: feature/{task}/payment-ui
(서브태스크 = PR 단위)
```
