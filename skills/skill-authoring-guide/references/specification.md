# Frontmatter Specification

agentskills.io 표준 기반 frontmatter 필드별 상세 스펙입니다.

---

## 필수 필드

### name

| 항목 | 규칙 |
|------|------|
| 형식 | kebab-case (lowercase + hyphens) |
| 최대 길이 | 64자 |
| 허용 문자 | `a-z`, `0-9`, `-` |
| 금지 | 연속 하이픈 (`--`), 시작/끝 하이픈 |
| 일치 | 디렉토리명과 반드시 동일 |

```yaml
# 유효
name: payment-webhook
name: db-migration-v2

# 무효
name: Payment_Webhook    # 대문자, 언더스코어
name: my--skill          # 연속 하이픈
name: -my-skill          # 시작 하이픈
name: a                  # 너무 짧아 의미 전달 불가 (권장사항)
```

### description

| 항목 | 규칙 |
|------|------|
| 최대 길이 | 1024자 |
| 인칭 | 3인칭 (주어 없이 동사로 시작) |
| 내용 | what (무엇을 하는지) + when (언제 사용하는지) |
| 금지 | 1인칭 ("I help you..."), 시간 의존 표현 |

```yaml
# 좋은 예
description: Processes payment webhooks and validates signatures when a new transaction event is received.
description: Guides the creation of new skills following the agentskills.io standard when authoring or reviewing skill files.

# 나쁜 예
description: I help you process payment webhooks.       # 1인칭
description: Processes webhooks.                         # when 누락
description: The latest webhook processor for 2025.      # 시간 의존
```

---

## 선택 필드

### license

SPDX 라이선스 식별자를 사용합니다.

```yaml
license: MIT
license: Apache-2.0
```

표준 SPDX 식별자 목록: https://spdx.org/licenses/

### compatibility

호환 플랫폼을 배열로 나열합니다.

```yaml
compatibility:
  - claude-code
  - cursor
```

### metadata

임의의 key-value 쌍을 저장합니다. 표준에서는 구조를 강제하지 않으며, 플랫폼/조직별로 자유롭게 확장 가능합니다.

```yaml
metadata:
  author: team-name
  version: "1.0.0"
  category: infrastructure
```

#### Workbench 전용 metadata 확장

Workbench에서는 다음 키를 `metadata` 하위에 배치합니다.

| 키 | 타입 | 설명 |
|----|------|------|
| `author` | string | 작성자 (보통 `workbench`) |
| `version` | string | 플러그인 버전 (semver) |
| `skills` | string[] | 의존 스킬 목록 |
| `agents` | string[] | 사용 에이전트 목록 |

```yaml
metadata:
  author: workbench
  version: "1.4.0"
  skills: [vault-conventions]
  agents: [analyzer]
```

> 기존 최상위 `skills:`, `agents:` 필드와의 호환: 기존 파서는 최상위 필드를 계속 읽습니다. 신규 스킬은 `metadata` 하위에 배치하되, 마이그레이션 전까지 두 형식 모두 허용됩니다.

### allowed-tools

스킬이 사용할 수 있는 도구를 명시적으로 제한합니다.

```yaml
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
```

지정하지 않으면 제한 없음 (모든 도구 사용 가능).

---

## SKILL.md 본문 규칙

| 항목 | 규칙 |
|------|------|
| 최대 줄 수 | 500줄 |
| 토큰 예산 | <5000 tokens (Instructions 단계) |
| 언어 | 프로젝트 언어 따름 (Workbench: 한국어, 코드/예시 제외) |
| 참조 깊이 | 1단계만 (SKILL.md -> references/xxx.md) |

### 본문에 포함할 것

- 스킬의 목적과 사용 시점
- 핵심 프로세스/절차
- 주요 규칙/제약조건
- references/ 참조 링크

### 본문에 포함하지 않을 것

- Claude가 이미 아는 일반 지식
- 시간에 의존하는 정보
- 다른 스킬의 내용 복사 (참조로 대체)
- 500줄을 넘기는 상세 설명 (references/로 분리)

---

## 디렉토리 구조 규칙

```
skill-name/
├── SKILL.md              # 필수
├── scripts/              # 선택: 실행 가능한 코드
│   └── validate.sh
├── references/           # 선택: 상세 참조 문서
│   ├── spec-detail.md
│   └── api-guide.md
└── assets/               # 선택: 템플릿, 설정 파일
    └── template.yaml
```

- `SKILL.md`는 디렉토리 루트에 위치 (필수)
- 하위 디렉토리는 모두 선택
- `references/` 파일은 SKILL.md에서만 참조됨 (상호 참조 금지)
- `scripts/`는 실행 코드, `assets/`는 비실행 리소스
