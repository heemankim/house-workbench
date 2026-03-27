---
name: knowledge-extract
description: Extracts reusable knowledge from completed tasks and saves to the resources folder. Use when finishing a task to capture learnings for future reference.
metadata:
  author: workbench
  version: "1.5.0"
---

# knowledge-extract: 지식 추출

태스크 완료 시 재사용 가능한 지식을 추출하여 3-Resources/에 저장합니다.

---

## 호출 시점

| 커맨드 | 동작 |
|--------|------|
| `wb-end` | 태스크 완료 시 자동 호출 |
| 수동 호출 | 진행 중에도 수동으로 지식 추출 가능 |

---

## 프로세스

### 입력

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| task_path | O | vault 내 태스크 경로 |

### 실행

```
1. 태스크 폴더 전체 읽기:
   - TASK.md (개요)
   - subtasks/*.md (작업지시서)
   - decisions.md (의사결정)
   - notes/ (메모)

2. 지식 후보 추출:
   a. 트러블슈팅: SUBTASK.md의 히스토리에서 문제→해결 패턴
   b. 패턴: 반복 사용된 기술적 접근법
   c. 의사결정: 다른 프로젝트에도 적용 가능한 결정

3. 각 후보에 대해 사용자 확인:
   "다음 지식을 3-Resources/에 저장할까요?"

4. 확인된 항목을 3-Resources/에 마크다운 파일로 생성
5. 원본 태스크에 wikilink 연결
```

### 추출 기준

| 기준 | 설명 |
|------|------|
| 재사용성 | 다른 프로젝트에서도 적용 가능한가? |
| 구체성 | 단순 의견이 아닌 구체적 절차/코드가 있는가? |
| 고유성 | vault에 이미 유사한 지식이 없는가? |

---

## 사용자 확인 UI

```
📚 지식 추출 후보 (3건):

1. [Pattern] PG 연동 모듈 패턴
   → NestJS에서 PG사 연동 시 모듈 구조
   → 저장: 3-Resources/patterns/pg-integration-pattern.md

2. [Troubleshoot] NestJS SQS Consumer 타임아웃
   → SQS 메시지 처리 시 타임아웃 해결법
   → 저장: 3-Resources/troubleshooting/nestjs-sqs-timeout.md

3. [Decision] JWT vs Session (범용)
   → 마이크로서비스 환경에서의 인증 방식 비교
   → 저장: 3-Resources/patterns/auth-jwt-vs-session.md

저장할 항목을 선택하세요 (번호, 쉼표 구분 / all / none):
```

---

## 저장 포맷

### 트러블슈팅 (3-Resources/troubleshooting/)

```markdown
---
type: resource
category: troubleshoot
tags: [nestjs, sqs]
created: 2026-02-19
source: "[[4-Archives/{task-name}/TASK]]"
---

# NestJS SQS Consumer 타임아웃

## TL;DR
SQS Consumer에서 30초 이상 걸리는 작업 시 visibility timeout을 늘려야 함.

## 증상
- 메시지가 중복 처리됨
- DLQ에 메시지 쌓임

## 원인
기본 visibility timeout(30s)이 처리 시간보다 짧음

## 해결
```ts
@SqsConsumerEventHandler(QUEUE_NAME, 'processing_error')
// visibilityTimeout: 120 설정
```

## 관련
- [[nestjs-module-pattern]]
- 출처: [[4-Archives/{task-name}/subtasks/01-pg-integration|서브태스크]]
```

### 패턴 (3-Resources/patterns/)

```markdown
---
type: resource
category: pattern
tags: [nestjs, payment]
created: 2026-02-19
source: "[[4-Archives/{task-name}/TASK]]"
---

# PG 연동 모듈 패턴

## TL;DR
NestJS에서 PG사 연동 시 추상화 레이어 + 전략 패턴 사용.

## 구조
{패턴 설명}

## 코드 예시
{핵심 코드}

## 적용 시 주의점
{주의사항}

## 관련
- [[auth-jwt-vs-session]]
- 출처: [[4-Archives/{task-name}/subtasks/01-pg-integration|서브태스크]]
```

---

## 중복 검사

저장 전 기존 vault 지식과 중복 확인:

```
1. 3-Resources/ 전체에서 유사 제목 Grep
2. 유사 문서 발견 시:
   a. 기존 문서에 추가할지
   b. 별도 문서로 생성할지
   사용자에게 확인
```

---

## summary.md 연동

knowledge-extract가 완료되면 summary.md에 추출 결과를 기록합니다:

```markdown
## 추출된 지식
- [[3-Resources/patterns/pg-integration-pattern]] (새로 생성됨)
- [[3-Resources/troubleshooting/nestjs-sqs-timeout]] (새로 생성됨)
- [[3-Resources/patterns/auth-jwt-vs-session]] (기존 문서에 추가됨)
```

---

## 활용 내역 표시

```
📊 knowledge-extract 완료
├─ 📖 분석: TASK.md, subtasks/ 3개, decisions.md
├─ 💡 후보: 5건 감지 → 3건 선택됨
├─ 📝 생성:
│   ├─ 3-Resources/patterns/pg-integration-pattern.md
│   └─ 3-Resources/troubleshooting/nestjs-sqs-timeout.md
├─ 📝 업데이트:
│   └─ 3-Resources/patterns/auth-jwt-vs-session.md (추가)
└─ ⏱️ 소요: 10초
```
