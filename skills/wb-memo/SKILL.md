---
name: wb-memo
description: Saves decisions, troubleshooting notes, and memos to the Obsidian vault with category tagging. Use when capturing important information for future recall.
metadata:
  author: workbench
  version: "1.5.0"
  skills:
    - vault-conventions
---

# wb-memo: Vault에 메모 저장

의사결정, 메모, 트러블슈팅 등을 vault에 저장합니다.

## 입력
- `$ARGUMENTS`: `[메모 내용]` (선택)

## 프로세스

### 1. 카테고리 선택

```
메모 유형:
  1. 의사결정 (Decision)
  2. 메모 (Note)
  3. 문제해결 (Troubleshooting)
  4. 패턴 (Pattern)
```

### 3. 내용 입력

```
$ARGUMENTS에서 내용 파싱
없으면 사용자에게 입력 요청
```

### 4. Vault에 저장

`vault-conventions`의 카테고리 → 경로 매핑에 따라 vault에 직접 저장합니다.

```
1. 카테고리별 저장 경로 결정 (vault-conventions 참조)
2. 기존 파일 존재 확인 (Glob)
3-a. 파일 존재: 기존 내용에 추가 (append)
3-b. 파일 없음: 새 파일 생성 (frontmatter + ## TL;DR 포함)
```

### 5. 완료 메시지

```
✅ 메모 저장됨

📝 유형: Decision
🏷️ 제목: JWT vs Session
💾 저장: {vault}/3-Resources/patterns/jwt-vs-session.md

/wb-recall로 검색할 수 있습니다.
```

### 6. Task 컨텍스트 자동 연결

현재 Task가 있으면 자동으로 컨텍스트를 연결합니다:

```
현재 Task: data/tasks/{task-name}/ 내부이면:
→ source_description에 "workbench task: {task-name} / subtask: {subtask-name}" 자동 추가
→ history/{date}.md에도 메모 기록 추가

현재 Task 없으면:
→ source_description: "workbench memo"
→ history 기록 없음
```

---

## 활용 내역 표시

```
📊 /wb-memo 실행 완료
├─ 📝 유형: {category}
├─ 💾 저장: {vault 경로}
├─ 🔗 Task 연결: {task-name} / {subtask-name} (있을 때만)
└─ ⏱️ 소요: {시간}
```
