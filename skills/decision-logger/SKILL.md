---
name: decision-logger
description: Detects and records architectural and technical decisions from conversations into the vault. Use when saving or completing subtasks to capture decision history.
metadata:
  author: workbench
  version: "1.5.0"
---

# decision-logger: 의사결정 자동 기록

대화 중 발생하는 의사결정을 감지하여 vault의 decisions.md에 자동 기록합니다.

---

## 감지 패턴

다음 패턴이 대화에서 감지되면 의사결정으로 간주합니다:

| 패턴 | 예시 |
|------|------|
| A vs B 비교 후 선택 | "JWT vs Session → JWT로 결정" |
| 명시적 결정 표현 | "~로 하겠습니다", "~로 가자" |
| 기술 선택 | "Redis 대신 인메모리 캐시 사용" |
| 아키텍처 결정 | "모놀리식으로 진행" |
| 방향 전환 | "처음에 A였지만 B로 변경" |

---

## 호출 시점

| 커맨드 | 동작 |
|--------|------|
| `wb-save` | 대화 내 의사결정 감지 시 자동 기록 |
| `wb-done` | 서브태스크 완료 시 미기록 결정 확인 |
| 수동 호출 | 사용자가 직접 결정 기록 요청 |

---

## 기록 프로세스

### 입력

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| title | O | 결정 제목 (예: "JWT vs Session") |
| decision | O | 결정 내용 |
| context | - | 결정 배경 |
| alternatives | - | 고려한 대안 |
| rationale | - | 선택 이유 |
| subtask | - | 관련 서브태스크 번호 |

### 실행

```
1. 활성 태스크 확인 (TASK.md → vaultPath)
2. vault/{task}/decisions.md 읽기
3. 새 결정 항목 추가
4. 서브태스크가 있으면 해당 SUBTASK.md의 의사결정 섹션에도 링크 추가
```

### decisions.md 기록 포맷

```markdown
## 2026-02-19: JWT vs Session {#JWT-vs-Session}

**서브태스크**: [[subtasks/01-pg-integration|01. PG 모듈 구현]]

**컨텍스트**
결제 모듈의 인증 방식 결정 필요

**결정**
JWT 토큰 방식 채택

**대안**
- Session 기반: 서버 상태 관리 필요
- OAuth2: 과도한 복잡성

**근거**
- 마이크로서비스 간 전파 용이
- 서버 stateless 유지
- 기존 인증 시스템과 호환

---
```

> heading에 `{#anchor}` ID를 부여하여 서브태스크에서 `[[decisions#JWT-vs-Session]]`로 참조합니다.

### SUBTASK.md 연동

서브태스크와 관련된 결정일 경우:

```markdown
## 의사결정
- [2026-02-19] JWT 방식 선택 → [[decisions#JWT-vs-Session|결정 상세]]
```

---

## 자동 감지 프로세스

`wb-save` 또는 `wb-done` 호출 시:

```
1. 현재 대화 내용 스캔
2. 의사결정 패턴 매칭
3. 감지된 결정이 있으면:
   a. 사용자에게 확인: "의사결정이 감지되었습니다. 기록할까요?"
   b. 확인 시 기록 실행
4. decisions.md에 이미 있는 내용은 중복 방지
```

### 감지 시 사용자 확인 UI

```
💡 의사결정 감지:
┌─────────────────────────────────────────┐
│ 제목: JWT vs Session                    │
│ 결정: JWT 토큰 방식 채택                 │
│ 서브태스크: #01 PG 모듈 구현             │
└─────────────────────────────────────────┘
decisions.md에 기록할까요? (Y/n/수정)
```

---

## 주의사항

1. **중복 방지**: 같은 결정을 두 번 기록하지 않도록 제목 유사도 확인
2. **사용자 확인**: 자동 감지된 결정은 반드시 사용자 확인 후 기록
3. **Obsidian 호환**: heading anchor ID는 Obsidian의 block reference와 호환
4. **히스토리 보존**: decisions.md는 append-only (삭제/수정은 수동으로만)
