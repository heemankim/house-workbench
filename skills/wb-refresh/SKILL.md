---
name: wb-refresh
description: Re-scans the vault and updates frontloaded knowledge in TASK.md and SUBTASK.md. Use when vault content has changed since the last scan.
metadata:
  author: workbench
  version: "1.5.0"
  skills:
    - vault-conventions
---

# wb-refresh: 프론트로딩 갱신

vault 변경을 감지하고 TASK.md/SUBTASK.md의 `## 관련 지식` 섹션을 다시 스캔하여 업데이트합니다.

## 입력
- `$ARGUMENTS`: 없음

## 언제 사용하나

wb-resume 시 staleness가 감지되면 안내됩니다:

```
💡 마지막 스캔 이후 5개 파일 변경됨.
   /wb-refresh로 관련 지식을 업데이트할 수 있습니다.
```

또는 사용자가 vault에 새 문서를 추가한 후 명시적으로 실행합니다.

## 프로세스

### 1. 현재 Task 확인

```
현재 Task: data/tasks/{task-name}/
vault 경로: 1-Projects/{task-name}/
```

### 2. 변경된 파일 감지

```bash
# TASK.md frontmatter의 lastScanned 이후 변경된 파일
find {vault}/3-Resources -name "*.md" -newer {timestamp_file} -type f
```

### 3. Vault 재검색

config.json `beta.fts-indexer` 확인 후 재검색:

```
FTS5 모드 (true):
  python3 tools/vault-search.py search "{query}" --vault {vault} --limit 10
  → JSON 결과에서 path, title, tldr 추출

grep 모드 (false/미설정):
  Stage 1: frontmatter tags grep (경로 힌트 적용)
  Stage 2: TL;DR 섹션 grep

대상: Task 목표 + 현재 서브태스크 키워드
```

### 4. TASK.md 업데이트

```markdown
## 관련 지식
- [[pg-integration-guide]] — PG 연동 가이드 (3-Resources)
- [[nestjs-module-pattern]] — NestJS 모듈 패턴 (3-Resources)
- [[new-troubleshooting]] — 새로 추가된 문서 ← NEW
```

### 5. 현재 SUBTASK.md 업데이트

현재 진행 중인 서브태스크의 `## 관련 지식`도 갱신합니다.

### 6. lastScanned 갱신

```yaml
---
lastScanned: 2026-03-04T15:30:00+09:00  # 갱신됨
---
```

### 7. 완료 메시지

```
✅ 프론트로딩 갱신 완료

📊 변경 감지: 5개 파일
📝 TASK.md: 관련 지식 1건 추가
📝 SUBTASK.md: 관련 지식 1건 추가
🕐 lastScanned: 2026-03-04T15:30:00+09:00
```

---

## 활용 내역 표시

```
📊 /wb-refresh 실행 완료
├─ 💾 Vault: 재검색 (변경 5개 파일)
├─ 📝 Updates:
│   ├─ TASK.md 관련 지식: +1건
│   └─ SUBTASK.md 관련 지식: +1건
├─ 🕐 lastScanned 갱신
└─ ⏱️ 소요: {시간}
```
