---
name: wb-start
description: Starts a new task by creating directory structure, analyzing requirements, and generating subtask drafts. Use when beginning a new project or feature.
metadata:
  author: workbench
  version: "2.1.0"
  skills:
    - vault-conventions
    - code-analysis
  agents:
    analyze: workbench:analyzer
---

# wb-start: Task 시작

새로운 Task를 시작하고 서브태스크 초안을 생성합니다.

## 입력
- `$ARGUMENTS`: Task 이름 (선택, 없으면 대화형)

## 프로세스

### 1. Task 이름 확인
```
$ARGUMENTS가 있으면 사용
없으면 사용자에게 질문
```

### 1.5. PLAN.md 감지

```
data/tasks/{task-name}/PLAN.md가 있으면:
→ "기존 분석 결과(PLAN.md)를 기반으로 세팅합니다"
→ 서브태스크를 PLAN.md의 태스크 분해에서 가져옴
→ 미확인 사항은 wait 타입 서브태스크로 자동 생성
→ 3단계(서브태스크 초안) 스킵하고 확인만 받음

없으면 기존 프로세스 진행
```

### 2. Task 유형 선택

```
📋 Task 유형을 선택하세요:

[1] code - 레포 기반 코드 작업
    → PR 생성, 브랜치 관리, worktree 사용
    → 예: 기능 개발, 버그 수정, 리팩토링

[2] ops - 운영/설정 작업
    → MCP 도구, 서버 설정, 자동화 구성
    → 예: n8n 워크플로우, 서버 설정, CI/CD 구성
```

### 3. Task 분석 및 서브태스크 초안

사용자에게 Task 목표를 물어보고 서브태스크를 제안합니다.
각 서브태스크에 적절한 유형을 자동 할당합니다.

**서브태스크 유형:**
| 유형 | 아이콘 | 용도 |
|------|--------|------|
| `code` | 📦 | 코드 작업 (PR) |
| `ops` | 🔧 | 운영/설정 작업 |
| `wait` | ⏳ | 대기/협의 (외부 의존) |
| `doc` | 📝 | 문서 작업 |
| `research` | 🔍 | 조사/분석 |

#### ⚠️ 서브태스크 확인 시 AskUserQuestion 사용 규칙

**중요**: VSCode에서 `preview` 필드와 `question` 줄바꿈이 렌더링되지 않습니다.
서브태스크 목록은 **"확정" 옵션의 `description`에 파이프(|) 구분**으로 넣으세요.

```
AskUserQuestion 호출 형식:

questions: [{
  question: "서브태스크 초안을 확인해주세요.",
  header: "Subtasks",
  options: [
    {
      label: "확정 (Recommended)",
      description: "01.📦 PG 모듈 구현 | 02.⏳ 정책 협의 | 03.📝 API 문서 | 04.📦 결제 UI←#2 | 05.🔧 배포←#4"
    },
    {
      label: "수정 필요",
      description: "서브태스크 추가/삭제/변경 요청"
    }
  ],
  multiSelect: false
}]
```

`description`에 `{번호}.{아이콘} {이름}` 형식을 파이프로 연결하면
옵션 선택 화면에서 서브태스크 목록을 한눈에 확인할 수 있습니다.

#### 예시: 혼합 서브태스크
```
AskUserQuestion description 예시:

"01.📦 PG 모듈 (backend) | 02.⏳ 정책 협의 | 03.📝 API 문서 | 04.📦 결제 UI←#2 | 05.⏳ QA 승인←#1,#4 | 06.🔧 배포←#5"
```

#### 의존성 설정

서브태스크 간 의존성을 설정하면 blocked 상태를 자동 관리합니다:
```
4. [📦 code] 결제 UI (frontend) ← depends: #2
   → #2 완료 전까지 blocked 상태
   → #2 완료 시 자동 unblock
```

---

## Code 유형 프로세스

### 4c. 레포 선택

`repos.json`에서 레포 목록을 읽어 첫 서브태스크에 필요한 레포 선택

### 5c. 브랜치명 결정

Workspace .claude/skills에서 브랜치 관련 규칙을 확인합니다.
없으면 기본 패턴 `feature/{task}/{subtask}` 사용.

생성된 브랜치명을 사용자에게 보여주고 확인/수정 받습니다.

### 6c. 폴더 구조 생성

> 이 단계 전에 vault TASK.md와 SUBTASK.md가 먼저 생성되어야 합니다 (9단계 참조).
> 실제 실행 순서: vault 생성(9) → 폴더 구조(6c) → worktree(7c)

```
data/tasks/{task-name}/
├── .claude -> ../../../.claude   # Workspace 커스텀 심볼릭 링크 (자동 생성)
├── CLAUDE.md                  # Task 컨텍스트 (레포 skills 참조)
├── TASK.md                    # 작업지시서 (frontmatter에 type, taskManager ID 포함)
├── subtasks/
│   ├── 01-pg-integration/     # 첫 서브태스크
│   │   ├── SUBTASK.md         # 최소 템플릿 (vault-conventions 참조)
│   │   └── {repo}/{branch}/   # worktree
│   ├── 02-payment-ui/
│   │   └── SUBTASK.md         # 최소 템플릿
│   └── 03-integration-test/
│       └── SUBTASK.md         # 최소 템플릿
└── history/
    └── YYYY-MM-DD.md
```

**심볼릭 링크 생성:**
```bash
# Workspace에 .claude가 있으면 자동으로 링크
if [ -d "../../../.claude" ]; then
    ln -s ../../../.claude data/tasks/{task-name}/.claude
fi
```

이 링크로 Task 폴더에서 VSCode를 열어도 Workspace 커스텀 commands/skills/agents 사용 가능.

### 7c. Worktree 생성 (첫 서브태스크만)

```bash
cd repos/{repo-name}
git fetch origin
git pull origin {defaultBase}
git worktree add ../../data/tasks/{task-name}/subtasks/01-xxx/{repo}/{branch} -b {branch}
```

> `{defaultBase}`는 repos.json의 `defaultBase` 값 (기본: main).
> pull로 로컬 base 브랜치를 최신 상태로 만든 후 worktree를 생성합니다.

### 7.5c. 모든 서브태스크에 최소 SUBTASK.md 생성

모든 서브태스크 폴더에 vault-conventions의 "SUBTASK.md 최소 템플릿"으로 파일을 생성합니다.
첫 서브태스크뿐 아니라 **모든** 서브태스크 폴더에 생성합니다.

> vault subtasks/ 디렉토리에도 동일한 SUBTASK.md를 생성합니다.

```
subtasks/01-pg-integration/SUBTASK.md   ← status: pending, subtask_type: code
subtasks/02-payment-ui/SUBTASK.md       ← status: pending, subtask_type: code
subtasks/03-integration-test/SUBTASK.md ← status: pending, subtask_type: code
```

- subtask_type, depends, repo 정보는 서브태스크 초안에서 추출
- PLAN.md 경로에서도 동일하게 적용

### 8c. 레포 .claude 감지 및 Task CLAUDE.md 생성

**중요**: 각 레포에 `.claude/` 폴더가 있는지 확인하고, Task의 CLAUDE.md에 참조 정보 추가.

레포에 .claude가 있으면:
```
💡 레포에 .claude 폴더 감지됨:

backend/.claude/skills/:
- api-patterns.md - API 설계 패턴
- test-guide.md - 테스트 작성 가이드

작업 시 이 파일들을 참조하세요.
CLAUDE.md에 경로가 기록됩니다.
```

Task의 CLAUDE.md 생성:
```markdown
# Task: 결제 기능
type: code

## 레포 Skills 참조

이 Task에서 사용하는 레포들의 .claude 폴더입니다.
작업 전 해당 레포의 skills를 확인하세요.

### backend
경로: `subtasks/01-pg-integration/backend/{branch}/.claude/`

Skills:
- [api-patterns](subtasks/01-pg-integration/backend/{branch}/.claude/skills/api-patterns/SKILL.md)
- [test-guide](subtasks/01-pg-integration/backend/{branch}/.claude/skills/test-guide/SKILL.md)
```

---

## Ops 유형 프로세스

### 4o. 도구 확인

사용할 MCP 도구나 외부 서비스를 확인:
```
🔧 이 Task에서 사용할 도구를 선택하세요:

사용 가능한 MCP 도구를 나열하여 선택:
[ ] (사용 가능한 MCP 도구 동적 표시)

외부 서비스:
[ ] 서버 (SSH/API)
[ ] 기타 (직접 입력)
```

### 5o. 폴더 구조 생성

> 이 단계 전에 vault TASK.md와 SUBTASK.md가 먼저 생성되어야 합니다 (9단계 참조).
> 실제 실행 순서: vault 생성(9) → 폴더 구조(5o) → 서브태스크 생성(5.5o)

```
data/tasks/{task-name}/
├── .claude -> ../../../.claude   # Workspace 커스텀 심볼릭 링크 (자동 생성)
├── CLAUDE.md                  # Task 컨텍스트
├── TASK.md                    # 작업지시서 (frontmatter에 type, taskManager ID 포함)
├── subtasks/
│   ├── 01-api-setup/
│   │   └── SUBTASK.md         # 최소 템플릿
│   ├── 02-workflow-create/
│   │   └── SUBTASK.md         # 최소 템플릿
│   └── 03-slack-integration/
│       └── SUBTASK.md         # 최소 템플릿
├── artifacts/                 # 생성된 결과물 (설정 파일, 스크린샷 등)
└── history/
    └── YYYY-MM-DD.md
```

**심볼릭 링크 생성:**
```bash
# Workspace에 .claude가 있으면 자동으로 링크
if [ -d "../../../.claude" ]; then
    ln -s ../../../.claude data/tasks/{task-name}/.claude
fi
```

### 5.5o. 모든 서브태스크에 최소 SUBTASK.md 생성

모든 서브태스크 폴더에 vault-conventions의 "SUBTASK.md 최소 템플릿"으로 파일을 생성합니다.

- subtask_type, depends 정보는 서브태스크 초안에서 추출
- ops 유형은 repo/branch 빈 문자열

### 6o. Task CLAUDE.md 생성 (ops)

```markdown
# Task: 날씨 자동화
type: ops

## 도구

이 Task에서 사용하는 도구들:

### MCP
- n8n-mcp: 워크플로우 자동화

### 외부 서비스
- OpenWeather API
- Slack Webhook

## 참고 Skills

워크스페이스 .claude/skills:
- [n8n-patterns](../../.claude/skills/n8n-patterns/SKILL.md)
- [slack-integration](../../.claude/skills/slack-integration/SKILL.md)
```

---

## 공통 프로세스

### ⚠️ Vault-First 원칙

모든 파일 생성은 **vault → data/tasks** 순서입니다:

```
1. vault 1-Projects/{task}/ 에 TASK.md 생성 (SSoT)
2. vault subtasks/ 에 SUBTASK.md 생성
3. data/tasks/{task}/ 에 경량 포인터 TASK.md 생성
4. data/tasks/ 에 worktree, history 등 작업 파일 생성
```

data/tasks/TASK.md는 `vaultPath` 포인터만 포함합니다.
실제 태스크 상태, 서브태스크 체크리스트, 의사결정은 모두 vault가 SSoT입니다.

### 9. Vault TASK.md 생성 (SSoT) + data/tasks 포인터

**순서**: vault TASK.md를 먼저 생성한 후, data/tasks/ 포인터를 생성합니다.

vault `1-Projects/{task-name}/TASK.md`를 생성합니다:

```yaml
---
type: code          # 또는 ops
created: YYYY-MM-DD
lastScanned: ISO-8601   # Vault 스캔 시점 (wb-resume staleness 감지용)
---

# Task: {task-name}

## 목표
{사용자 입력}

## 서브태스크
- [ ] 01. {서브태스크1} → [[subtasks/01-name]]
- [ ] 02. {서브태스크2} → [[subtasks/02-name]]

## 관련 지식
> wb-start 시 Vault 검색 결과가 여기에 임베딩됩니다.
> wb-resume 시 이 섹션을 읽어 vault 재검색 없이 컨텍스트를 복원합니다.
```

`data/tasks/{task-name}/TASK.md`는 경량 포인터만 생성합니다:

```yaml
---
type: code
vaultPath: "1-Projects/{task-name}"
---
```

### 10. Vault 동기화

vault TASK.md 체크리스트와 SUBTASK.md 상태를 직접 업데이트합니다.
(vault-conventions 스키마에 따라 체크리스트 형식 적용)

### 11. Vault 검색 및 프론트로딩

vault에서 관련 지식을 검색하고 **TASK.md `## 관련 지식` 섹션에 임베딩**합니다.

```
config.json `beta.fts-indexer` 확인:

FTS5 모드 (true):
  python3 tools/vault-search.py search "{query}" --vault {vault} --limit 10
  → JSON 결과에서 path, title, tldr 추출

grep 모드 (false/미설정):
  Stage 1: frontmatter tags grep (경로 힌트 적용)
  Stage 2: TL;DR 섹션 grep

결과를 TASK.md에 기록:
## 관련 지식
- [[pg-integration-guide]] — PG 연동 가이드 (3-Resources)
- [[nestjs-module-pattern]] — NestJS 모듈 패턴 (3-Resources)

lastScanned 타임스탬프 갱신
```

이후 wb-resume 시 vault를 재검색하지 않고 이 섹션만 읽습니다.

### 12. 완료 메시지

#### code 유형
```
┌─────────────────────────────────────────────────────────┐
│ ✅ Task 시작: {task-name}                                │
│ 📦 유형: code                                           │
├─────────────────────────────────────────────────────────┤
│ 📁 경로: data/tasks/{task-name}                            │
│ 📋 서브태스크: 3개                                       │
│ 🌿 현재 브랜치: feature/{task-name}/pg-integration       │
│                                                         │
│ 📚 레포 Skills 감지됨:                                   │
│  ├─ backend: api-patterns.md, test-guide.md             │
│  └─ frontend: component-guide.md                        │
│                                                         │
│ 💡 작업 전 CLAUDE.md의 "레포 Skills 참조" 확인           │
└─────────────────────────────────────────────────────────┘

다음 단계:
1. 작업을 진행하세요
2. /wb-done으로 서브태스크 완료
3. /wb-next로 다음 서브태스크

💡 독립 서브태스크가 2개 이상이면:
   /wb-run으로 병렬 실행 가능
```

#### ops 유형
```
┌─────────────────────────────────────────────────────────┐
│ ✅ Task 시작: {task-name}                                │
│ 🔧 유형: ops                                            │
├─────────────────────────────────────────────────────────┤
│ 📁 경로: data/tasks/{task-name}                            │
│ 📋 서브태스크: 4개                                       │
│ 🛠️ 도구: n8n-mcp, Slack Webhook                         │
│                                                         │
│ 📚 Workspace Skills:                                    │
│  ├─ n8n-patterns.md                                     │
│  └─ slack-integration.md                                │
│                                                         │
│ 💡 관련 기억 2건 검색됨                                  │
└─────────────────────────────────────────────────────────┘

다음 단계:
1. 첫 서브태스크를 진행하세요
2. /wb-done으로 서브태스크 완료
3. /wb-next로 다음 서브태스크

💡 독립 서브태스크가 2개 이상이면:
   /wb-run으로 병렬 실행 가능
```

## 활용 내역 표시

커맨드 실행 후 사용된 리소스를 표시:

#### code 유형
```
📊 /wb-start 실행 완료
├─ 📦 Type: code
├─ 🤖 Agents: analyzer (opus) - 서브태스크 분석
├─ 💾 Vault: 검색 + TASK.md 임베딩 (관련 지식 3건)
├─ 📚 Skills: vault-conventions
├─ 🔧 Actions:
│   ├─ Task 폴더 생성
│   ├─ Worktree 생성 (backend@feature/payment/pg)
│   └─ TASK.md, CLAUDE.md 생성
└─ ⏱️ 소요: 12초
```

#### ops 유형
```
📊 /wb-start 실행 완료
├─ 🔧 Type: ops
├─ 🤖 Agents: analyzer (opus) - 서브태스크 분석
├─ 💾 Vault: 검색 + TASK.md 임베딩 (관련 지식 2건)
├─ 📚 Skills: vault-conventions
├─ 🛠️ Tools: n8n-mcp (활성화됨)
├─ 🔧 Actions:
│   ├─ Task 폴더 생성
│   └─ TASK.md, CLAUDE.md 생성
└─ ⏱️ 소요: 8초
```
