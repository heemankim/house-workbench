---
name: wb-recall
description: Searches the Obsidian vault for past decisions, troubleshooting records, and stored knowledge. Use when needing to retrieve previously saved information.
metadata:
  author: workbench
  version: "1.5.0"
  skills:
    - vault-conventions
---

# wb-recall: Vault에서 검색

Vault에서 과거 기록을 검색합니다.

## 입력
- `$ARGUMENTS`: `[검색어]` (선택)

## 프로세스

### 1. 검색어 입력

```
$ARGUMENTS에서 검색어 파싱
없으면 사용자에게 입력 요청
```

### 2. Vault 검색

```
config.json `beta.fts-indexer` 확인:

FTS5 모드 (true):
  python3 tools/vault-search.py search "{query}" --vault {vault} --limit 20
  → JSON 결과에서 path, title, tldr, rank 추출
  → rank 기반 관련도순 정렬
  (3-stage 분리 불필요 — FTS5가 전체 인덱스를 단일 검색)

grep 모드 (false/미설정):
  Stage 1: frontmatter tags grep (경로 힌트 적용)
    vault-conventions의 경로 힌트 참조
  Stage 2: TL;DR 섹션 grep
  Stage 3: 전체 vault grep (wb-recall에서만 허용)
    다른 커맨드에서는 Stage 2까지만 수행
```

매칭 파일의 frontmatter + TL;DR 읽기 (파일 전체 불필요).
관련도순 정렬 (FTS5: rank순, grep: Stage 1 > Stage 2 > Stage 3).

### 3. 결과 표시

```
🔍 검색 결과: "{검색어}" ({N}건)

1. [Decision] JWT vs Session - 2024-01-15
   경로: 3-Resources/patterns/jwt-vs-session.md
   → 보안 요구사항으로 세션 방식 선택...

2. [Troubleshoot] 토큰 만료 처리 - 2024-01-10
   경로: 3-Resources/troubleshooting/token-expiry.md
   → 리프레시 토큰 로직 수정...
```

### 결과 없음 시

```
🔍 "{검색어}"에 대한 결과가 없습니다.

💡 다른 검색어를 시도하거나, /wb-memo로 새 메모를 저장하세요.
```

### Task 컨텍스트 활용

현재 Task 내부에서 실행하면 자동으로 컨텍스트를 활용합니다:

```
현재 Task: data/tasks/{task-name}/ 내부이면:
→ 검색어가 없어도 현재 Task 관련 vault 파일을 자동 검색
→ 결과에서 현재 Task 관련 항목을 상단에 표시

현재 Task 없으면:
→ 검색어 필수 (없으면 입력 요청)
→ 전체 vault에서 검색
```

---

## 활용 내역 표시

```
📊 /wb-recall 실행 완료
├─ 🔍 검색어: "{검색어}"
├─ 📊 결과: {N}건
├─ 🔗 Task 컨텍스트: {task-name} (있을 때만)
└─ ⏱️ 소요: {시간}
```
