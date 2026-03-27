# Examples

좋은/나쁜 예시 모음입니다. Workbench 스킬 기준으로 작성되었습니다.

---

## Frontmatter 예시

### 좋은 예: 표준 준수 + Workbench 확장

```yaml
---
name: payment-webhook
description: Processes incoming payment webhook events and validates their signatures when a new transaction notification arrives from the payment gateway.
metadata:
  author: workbench
  version: "1.4.0"
  skills: [vault-conventions]
  agents: [analyzer]
---
```

분석:
- `name`: kebab-case, 디렉토리명 일치
- `description`: 3인칭, what (Processes ... validates) + when (when ... arrives)
- `metadata`: 표준 필드 하위에 Workbench 확장 배치

### 좋은 예: 최소한의 필수 필드

```yaml
---
name: branch-rules
description: Enforces branch naming conventions and validates branch operations when creating or switching branches in a repository.
---
```

분석:
- 선택 필드 없이 필수 필드만으로 유효
- description이 충분히 설명적

### 나쁜 예: 흔한 실수들

```yaml
---
# 실수 1: name이 대문자 포함
name: PaymentWebhook

# 실수 2: description이 1인칭
description: I help you manage payment webhooks and validate signatures.

# 실수 3: skills가 최상위에 위치 (기존 방식, 비표준)
skills:
  - vault-conventions
---
```

수정:
```yaml
---
name: payment-webhook
description: Manages payment webhooks and validates signatures when processing transaction events.
metadata:
  skills: [vault-conventions]
---
```

---

## Description 예시

### 좋은 description

| 스킬 | description |
|------|-------------|
| vault-conventions | Obsidian vault PARA structure conventions and formats for all vault operations. |
| code-analysis | Performs symbolic code analysis using Serena MCP tools when commands require codebase exploration or impact assessment. |

| worktree-guard | Prevents direct modifications to files under the repos/ directory and enforces worktree-based workflows when code changes are attempted. |

패턴: `{동사} {목적어} {수단/방법} when {사용 시점}.`

### 나쁜 description

| description | 문제 |
|-------------|------|
| "Manages tasks." | 너무 짧음, when 누락 |
| "I manage task states for you." | 1인칭 |
| "The best task manager for 2025." | 시간 의존, 마케팅 문구 |
| "Task management" | 문장이 아님, 동사 없음 |
| "This skill helps manage tasks and also does memory and code analysis and..." | 범위 초과, 단일 책임 위반 |

---

## Progressive Disclosure 예시

### 1단계: Metadata (~100 tokens)

에이전트가 스킬 목록을 스캔할 때 로드되는 정보입니다.

```yaml
name: payment-webhook
description: Processes incoming payment webhook events and validates their signatures when a new transaction notification arrives.
```

이 정보만으로 "이 스킬이 현재 작업에 필요한가?"를 판단할 수 있어야 합니다.

### 2단계: Instructions (<5000 tokens)

SKILL.md 본문이 로드됩니다. 간결하게 핵심만 포함합니다.

```markdown
# payment-webhook: 결제 웹훅 처리

PG사에서 수신되는 결제 웹훅을 검증하고 처리합니다.

## 검증 프로세스
1. 서명 검증 (HMAC-SHA256)
2. 이벤트 타입 확인
3. 멱등성 키 확인
4. 비즈니스 로직 실행

## 지원 이벤트
| 이벤트 | 처리 |
|--------|------|
| payment.completed | 결제 완료 처리 |
| payment.failed | 실패 알림 |
| refund.completed | 환불 처리 |

> 상세 스펙: [references/webhook-spec.md](references/webhook-spec.md)
```

### 3단계: Resources (필요시)

`references/webhook-spec.md`는 에이전트가 실제로 웹훅 코드를 작성할 때만 로드됩니다.

---

## SKILL.md 본문 패턴

### 체크리스트 패턴 (절차형 스킬)

```markdown
## 프로세스
- [ ] 입력 파라미터 확인
- [ ] 설정 파일 읽기 (config.json)
- [ ] 대상 서비스 호출
- [ ] 결과 검증
- [ ] 상태 업데이트
```

### 라우팅 패턴 (어댑터/매니저 스킬)

```markdown
## 라우팅

config.json의 `adapters.type` 값에 따라 분기:

| type | 어댑터 | 설명 |
|------|--------|------|
| `todoist` | todoist-adapter/SKILL.md | Todoist API |
| `tududi` | tududi-adapter/SKILL.md | Tududi REST |
```

### 규칙 패턴 (가드/검증 스킬)

```markdown
## 규칙

### 허용
- worktree 경로에서의 파일 수정
- 새 브랜치 생성

### 금지
- repos/ 직접 수정
- main/master 브랜치에 직접 커밋
```

---

## 디렉토리 구조 예시

### 단순 스킬 (references 없음)

```
branch-rules/
└── SKILL.md
```

### 표준 스킬 (references 포함)

```
vault-conventions/
├── SKILL.md
└── references/
    ├── vault-mode.md
    └── adapter-mode.md
```

### 복합 스킬 (scripts + assets)

```
code-analysis/
├── SKILL.md
├── scripts/
│   └── analyze.sh
├── references/
│   └── serena-api.md
└── assets/
    └── analysis-template.md
```
