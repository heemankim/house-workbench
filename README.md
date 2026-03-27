# House Workbench

Context management framework for AI agent workflows

AI 에이전트 작업을 위한 컨텍스트 관리 프레임워크 (v2.1.0)

Claude Code와 함께 대규모 작업을 체계적으로 관리하고, 컨텍스트를 보존하며, 지식을 축적합니다.

---

> **Workbench** organizes complex AI-agent tasks into subtasks with isolated git worktrees, persists context across sessions via Obsidian vault, and accumulates reusable knowledge as Skills. Built as a [Claude Code](https://claude.ai/code) plugin.

---

## 해결하는 문제

| 문제 | Workbench 해결책 |
|------|------------------|
| 큰 작업 시 컨텍스트 터짐 | 서브태스크로 분리, 각각 독립 브랜치 |
| 병렬 작업 시 서로 섞임 | Task별 에이전트 분리 |
| 작업 중단 후 맥락 유실 | Obsidian vault + AI Memory로 영속 |
| 리뷰 불가능할 정도로 큰 변경 | 서브태스크 = PR 단위 |
| 같은 실수 반복 | 지식 축적 → Skills로 재사용 |

---

## 핵심 원칙

> **"전체 맥락은 공유, 각 Task는 분리, 컨텍스트는 보존"**

```
┌─────────────────────────────────────────────────────────────┐
│                    Workspace (work)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ .claude/skills/  ← 모든 Task가 공유하는 지식         │   │
│  │ (레포 정보, 패턴, 컨벤션)                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Task A    │  │   Task B    │  │   Task C    │        │
│  │  (결제기능)  │  │ (로그인버그) │  │  (회원탈퇴)  │        │
│  │             │  │             │  │             │        │
│  │ 서브태스크1  │  │ 서브태스크1  │  │ 서브태스크1  │        │
│  │ 서브태스크2  │  │     ...     │  │     ...     │        │
│  │ 서브태스크3  │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│        ↑                ↑                ↑                 │
│        └────── 각각 분리된 컨텍스트 ──────┘                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 계층 구조

```
Workspace (work, personal, side-project)
│
├── .claude/skills/      ← Workspace 지식 (모든 Task 공유)
│
├── vault/               ← Obsidian PARA (Task/Memory 저장소)
│   ├── 1-Projects/      ← 활성 Task
│   ├── 2-Areas/         ← 영역별 지식
│   ├── 3-Resources/     ← AI Memory (재사용 지식)
│   └── 4-Archives/      ← 완료된 Task
│
└── Task (결제 기능)      ← 1-Projects/의 프로젝트
    │
    ├── 서브태스크 1 (PG 연동)     ← = PR 단위
    │   └── worktree/
    │       └── backend/feature-pg/
    │
    ├── 서브태스크 2 (결제 UI)     ← = PR 단위
    │   └── worktree/
    │       └── frontend/feature-ui/
    │
    └── 서브태스크 3 (통합 테스트)  ← = PR 단위
        └── worktree/
            ├── backend/feature-test/
            └── frontend/feature-test/
```

**서브태스크 = PR 단위 = 리뷰 가능한 단위**

같은 레포를 여러 서브태스크에서 사용하면, 각각 다른 브랜치로 분리됩니다.

---

## Task 유형

Workbench는 두 가지 Task 유형을 지원합니다.

### Code 유형

레포 기반 코드 작업을 위한 유형입니다.

```
/wb-start "결제 기능"
→ [1] code 선택

📦 특징:
├─ PR 생성, 브랜치 관리, worktree 사용
├─ 서브태스크 = PR 단위
├─ git worktree로 격리된 작업 환경
└─ 레포 .claude 폴더 자동 감지

🎯 적합한 작업:
├─ 기능 개발
├─ 버그 수정
├─ 리팩토링
└─ 테스트 작성
```

### Ops 유형

운영/설정 작업을 위한 유형입니다. 레포 없이도 Task 관리가 가능합니다.

```
/wb-start "날씨 자동화"
→ [2] ops 선택

🔧 특징:
├─ MCP 도구, 서버 설정, 자동화 구성
├─ 서브태스크 = 체크리스트 단위
├─ artifacts/ 폴더에 결과물 저장
└─ 사용된 도구 자동 기록

🎯 적합한 작업:
├─ n8n 워크플로우 구성
├─ 서버 설정/배포
├─ CI/CD 파이프라인 구성
└─ 외부 서비스 연동
```

### 비교

| 항목 | Code | Ops |
|------|------|-----|
| **레포 필요** | 필수 | 선택 |
| **서브태스크 단위** | PR | 체크리스트 |
| **작업 환경** | git worktree | artifacts/ 폴더 |
| **완료 기준** | PR merged | 작업 완료 확인 |
| **결과물** | 코드 변경 | 설정, 워크플로우, 문서 |
| **기록 방식** | 커밋 로그 | 히스토리 + 결과물 |

### 지식 축적

두 유형 모두 동일한 지식 축적 흐름을 따릅니다:

```
작업 중 의사결정/트러블슈팅
         │
         ▼
    AI Memory 저장 (자동)
         │
         ▼
    다음 Task 시작 시 자동 검색
         │
         ▼
    /wb-save-skill로 영구 지식화
```

---

## 서브태스크 유형

하나의 Task 안에 다양한 유형의 서브태스크가 혼합될 수 있습니다.

### 유형 목록

| 유형 | 아이콘 | 용도 | 완료 기준 | 결과물 |
|------|--------|------|----------|--------|
| `code` | 📦 | 코드 작업 | PR merged | 코드 변경 |
| `ops` | 🔧 | 운영/설정 | 작업 완료 | 설정, 워크플로우 |
| `wait` | ⏳ | 대기/협의 | 외부 응답/승인 | 결정 사항, 회의록 |
| `doc` | 📝 | 문서 작업 | 문서 완성 | 기획서, 문서 |
| `research` | 🔍 | 조사/분석 | 결론 도출 | 분석 결과 |

### 서브태스크 상태

| 표기 | 상태 | 설명 |
|------|------|------|
| `- [ ]` | pending | 대기 |
| `- [ ] ⏳` | in_progress | 진행중 |
| `- [x] ✅ {날짜}` | done | 완료 |
| `- [ ] 🚫` | blocked | 의존성 미충족 |
| `- [~] (건너뜀: {사유})` | skipped | 건너뜀 |
| `- [-] (취소: {사유})` | cancelled | 취소됨 |

### 예시: 혼합 서브태스크

```
📋 Task: 결제 기능 v2

1. [📦 code] PG 모듈 구현 (backend)
2. [⏳ wait] 정책 협의 (기획팀) - 수수료율, 한도
3. [📝 doc] API 문서 작성
4. [📦 code] 결제 UI (frontend) ← depends: #2
5. [⏳ wait] QA 테스트 승인 ← depends: #1, #4
6. [🔧 ops] 프로덕션 배포 ← depends: #5
```

### 유형별 동작

#### code (📦)
```
/wb-done → 커밋 확인 → /wb-pr → PR 생성
결과물: PR #123
```

#### ops (🔧)
```
/wb-done → 작업 결과 확인 → artifacts/ 저장
결과물: n8n workflow #42
```

#### wait (⏳)
```
상태: pending → waiting → done
/wb-done → 결과 입력 (결정 사항, 회의록)
결과물: "수수료율 2.5%로 결정" (AI Memory 저장)

💡 대기 완료 시 blocked 서브태스크 자동 unblock
```

#### doc (📝)
```
/wb-done → 문서 링크/경로 입력
결과물: Notion 링크, Google Docs, Confluence 등
```

#### research (🔍)
```
/wb-done → 조사 결과/결론 입력
결과물: 분석 리포트, 기술 검토 문서
```

### 서브태스크 의존성

서브태스크 간 의존성을 설정할 수 있습니다:

```
📋 서브태스크:
1. [📦] PG 모듈 구현
2. [⏳] 정책 협의 ← 대기 중
3. [📝] API 문서 (depends: #1)
4. [📦] 결제 UI (depends: #2) ← blocked
5. [⏳] QA 승인 (depends: #1, #4)
6. [🔧] 배포 (depends: #5)
```

`#2 정책 협의` 완료 시 → `#4 결제 UI` 자동 unblock

---

## 라이프사이클

```
┌──────────────────────────────────────────────────────────────────┐
│                        Task 라이프사이클                          │
└──────────────────────────────────────────────────────────────────┘

/wb-start "결제 기능"
    │
    ├── 1. Task 분석 & 서브태스크 초안 생성
    ├── 2. Vault에 TASK.md + SUBTASK.md 생성
    ├── 3. AI Memory에서 관련 지식 검색
    └── 4. 모든 서브태스크에 SUBTASK.md 생성 + 첫 worktree 생성

         ↓

┌──────────────────────────────────────────────────────────────────┐
│                     서브태스크 사이클                              │
│                                                                  │
│   작업 ──→ /wb-save ──→ 작업 ──→ /wb-done ──→ /wb-pr            │
│     ↑                              │                             │
│     │                              ↓                             │
│     │         /wb-next ←──── 다음 서브태스크                      │
│     │              │                                             │
│     └──────────────┘                                             │
└──────────────────────────────────────────────────────────────────┘

         ↓ (모든 서브태스크 완료)

/wb-end
    │
    ├── 1. 전체 요약 생성
    ├── 2. AI Memory에 저장 (의사결정, 트러블슈팅)
    ├── 3. 반복 패턴 → Skill로 승격 (선택)
    └── 4. 1-Projects/ → 4-Archives/ 이동
```

### 명령어 요약

**초기화**
| 명령어 | 역할 |
|--------|------|
| `/wb-init` | Workspace 초기화 (config.json, repos.json 생성) |
| `/wb-add-repo` | 레포 등록 및 클론 |

**Task 라이프사이클**
| 명령어 | 시점 | 역할 |
|--------|------|------|
| `/wb-start` | Task 시작 | 서브태스크 계획, 모든 서브태스크에 SUBTASK.md 생성, 첫 worktree 생성 |
| `/wb-plan` | Task 분석 | PRD 기반 서브태스크 분해, 작업 계획 수립 |
| `/wb-save` | 작업 중 | 진행상황 저장 (세션 종료 전) |
| `/wb-check` | 완료 전 | 설계-구현 검증, Match Rate 계산 |
| `/wb-done` | 서브태스크 완료 | 커밋 정리, 의사결정 기록, SUBTASK.md 가드레일 |
| `/wb-pr` | PR 생성 | 서브태스크 → PR |
| `/wb-next` | 다음 서브태스크 | 새 브랜치, worktree 생성, SUBTASK.md 존재 확인 |
| `/wb-run` | 병렬 실행 | 독립 서브태스크 동시 실행 |
| `/wb-resume` | 이어서 작업 | 컨텍스트 복원, SUBTASK.md 존재 확인 |
| `/wb-end` | Task 완료 | 요약, 지식 저장, 아카이브 |
| `/wb-status` | 언제든 | 현재 상태 확인 |
| `/wb-update` | 업데이트 후 | 플러그인 버전 마이그레이션 |

**지식 관리**
| 명령어 | 역할 |
|--------|------|
| `/wb-add-subtask` | 서브태스크 동적 추가 (SUBTASK.md 원자적 생성) |
| `/wb-memo` | AI Memory에 메모 저장 |
| `/wb-recall` | AI Memory에서 검색 |
| `/wb-save-skill` | 패턴을 Skill로 저장 |

---

## 지식 축적 흐름

```
작업 중 의사결정/트러블슈팅
         │
         ▼
    AI Memory 저장 (자동)
    "PG webhook 타임아웃 30초로 설정"
         │
         ▼
    다음 Task 시작 시 자동 검색
    "💡 관련 기억: PG webhook 설정법"
         │
         ▼
    반복되는 패턴 발견
         │
         ▼
    /wb-save-skill "pg-webhook"
         │
         ▼
    .claude/skills/pg-webhook/SKILL.md 생성
    (영구 지식, /pg-webhook으로 호출)
```

**지식 계층:**
| 계층 | 저장소 | 수명 | 용도 |
|------|--------|------|------|
| 세션 내 | 현재 대화 | 휘발 | 즉시 작업 |
| Task 내 | vault 1-Projects/ | Task 기간 | 이어서 작업 |
| Task 간 | vault 3-Resources/ | 영구 | 자동 검색 |
| 영구 지식 | .claude/skills/*.md | 영구 | 명시적 호출 |

---

## 설치

Workbench는 Claude Code 로컬 플러그인으로 설치합니다.

### 1. 레포 클론

```bash
git clone https://github.com/heemankim/house-workbench.git ~/.workbench/core
```

### 2. 로컬 마켓플레이스 등록 및 설치

Claude Code에서:
```
/plugin marketplace add ~/.workbench/core
/plugin install workbench@workbench-local
```

### 3. 설치 확인

```
/plugin list
```

**설치 결과:**
```
~/.claude/plugins/cache/workbench-local/workbench/{version}/
├── skills/                     # /wb-* 커맨드 + 내부 스킬 (30개)
├── agents/                     # 공통 에이전트 (5개)
├── hooks/                      # 공통 훅
└── migrations/                 # 버전 마이그레이션 가이드
```

### 4. Workspace 설정

각 Workspace에서 `/wb-init`을 실행하거나 수동으로 설정합니다:

```bash
mkdir -p ~/Workspaces/work
cd ~/Workspaces/work
git init

# Workspace 커스텀 폴더
mkdir -p .claude/skills .claude/agents

# 기본 설정 파일
cat > config.json << 'EOF'
{
  "name": "work",
  "vault": "obsidian",
  "defaults": {
    "baseBranch": "main",
    "branchPrefix": "feature/"
  },
  "pluginVersion": "2.0.0"
}
EOF

cat > repos.json << 'EOF'
{
  "repos": []
}
EOF

# Obsidian vault 구조 (PARA)
mkdir -p obsidian/{1-Projects,2-Areas,3-Resources,4-Archives}

cat > .gitignore << 'EOF'
repos/
data/tasks/
.env
.DS_Store
EOF

git add .
git commit -m "Initial workspace setup"
```

### 5. 업데이트

```bash
# Core 저장소 업데이트
cd ~/.workbench/core && git pull

# 플러그인 업데이트 (Claude Code에서)
/plugin update workbench

# 마이그레이션 적용 (필요 시)
/wb-update
```

---

## 설정 (config.json)

### 기본 구조

```json
{
  "name": "work",
  "vault": "obsidian",
  "defaults": {
    "baseBranch": "main",
    "branchPrefix": "feature/"
  },
  "pluginVersion": "2.0.0"
}
```

| 필드 | 필수 | 설명 | 예시 |
|------|------|------|------|
| `name` | | Workspace 이름 | `"work"`, `"personal"` |
| `vault` | | Obsidian vault 경로 (workspace 기준 상대경로) | `"obsidian"` |
| `defaults.baseBranch` | | 기본 베이스 브랜치 | `"main"`, `"develop"` |
| `defaults.branchPrefix` | | 브랜치 접두사 | `"feature/"` |
| `pluginVersion` | | 설치된 플러그인 버전 | `"2.0.0"` |

### Vault 통합

`vault` 필드가 설정되면 Obsidian PARA vault를 통해 Task와 지식을 관리합니다.

```
config.json의 "vault" 필드
    │
    ├── Task 관리 → vault/1-Projects/, vault/4-Archives/
    └── AI Memory → vault/3-Resources/, vault/2-Areas/
```

### Obsidian Vault 구조 (PARA)

```
{workspace}/{vault}/
├── 1-Projects/{task-name}/          # 활성 태스크
│   ├── TASK.md                      # 태스크 개요 + 서브태스크 인덱스
│   ├── subtasks/                    # 서브태스크별 작업지시서
│   │   ├── 01-pg-integration.md
│   │   └── 02-payment-ui.md
│   ├── decisions.md                 # 의사결정 로그
│   └── notes/                       # 자유 노트
│
├── 2-Areas/                         # 영역별 상시 지식
│
├── 3-Resources/                     # AI Memory 재사용 지식
│
└── 4-Archives/{task-name}/          # 완료된 태스크 (전체 보존)
    ├── TASK.md
    ├── subtasks/
    ├── decisions.md
    └── summary.md                   # wb-end 시 자동 생성
```

---

## 레포 구성 (repos.json)

작업할 레포들을 `repos.json`에 등록합니다.

### 기본 구조

```json
{
  "repos": [
    {
      "name": "backend",
      "remote": "git@github.com:company/backend.git",
      "defaultBase": "develop",
      "branchPrefix": "feature/"
    },
    {
      "name": "frontend",
      "remote": "git@github.com:company/frontend.git",
      "defaultBase": "develop",
      "branchPrefix": "feature/"
    }
  ]
}
```

### 필드 설명

| 필드 | 필수 | 설명 | 예시 |
|------|------|------|------|
| `name` | ✅ | 레포 식별자 (폴더명) | `"backend"` |
| `remote` | ✅ | Git 원격 URL | `"git@github.com:company/backend.git"` |
| `defaultBase` | | 기본 베이스 브랜치 | `"develop"`, `"main"` |
| `branchPrefix` | | 브랜치 접두사 | `"feature/"`, `"fix/"` |
| `labels` | | 분류 태그 | `["api", "node"]` |

### 폴더 구조

```
~/Workspaces/work/
├── repos/                    ← 원본 레포 (gitignore)
│   ├── backend/              ← git clone 결과
│   │   └── .git/
│   └── frontend/
│       └── .git/
│
└── data/tasks/               ← worktree (gitignore)
    └── payment-feature/
        └── subtasks/
            └── 01-pg/
                └── backend/
                    └── feature-pg/  ← git worktree
```

**repos/**: 원본 레포 (항상 최신 상태 유지)
**data/tasks/**: 작업용 worktree (Task별로 분리)

### 레포의 .claude 폴더

레포 자체에 `.claude/` 폴더가 있을 수 있습니다 (팀 공유 skills):

```
repos/backend/
├── .claude/
│   └── skills/
│       ├── api-patterns.md    ← 팀 API 설계 패턴
│       └── test-guide.md      ← 팀 테스트 가이드
├── src/
└── ...
```

**`/wb-start` 시 자동 감지:**
- 선택한 레포에 `.claude/` 폴더가 있으면 감지
- Task의 `CLAUDE.md`에 참조 경로 자동 기록
- 작업 시 해당 skills를 참조하라고 안내

---

## Workspace 구조

플러그인 기반 아키텍처:

```
~/.claude/plugins/cache/workbench-local/   # 플러그인 (Core) - 모든 프로젝트 공유
└── workbench/{version}/
    ├── skills/                            # /wb-* 커맨드 + 내부 스킬 (30개)
    ├── agents/                            # 공통 에이전트 (5개)
    ├── hooks/                             # 공통 훅
    └── migrations/                        # 버전 마이그레이션

~/Workspaces/{name}/                       # Workspace (커스텀 추가)
├── .claude/
│   ├── skills/                            # Workspace 전용 스킬/커맨드
│   │   ├── zb-deploy/SKILL.md
│   │   └── zb-api-patterns/SKILL.md
│   └── agents/                            # Workspace 전용 에이전트
│       └── zb-reviewer.md
│
├── config.json                            # Workspace 설정
├── repos.json                             # 레포 목록
│
├── {vault}/                               # Obsidian vault (PARA)
│   ├── 1-Projects/                        # 활성 Task
│   ├── 2-Areas/                           # 영역별 지식
│   ├── 3-Resources/                       # AI Memory
│   └── 4-Archives/                        # 완료된 Task
│
├── repos/                                 # 원본 레포 (gitignore)
│   ├── backend/
│   │   └── .claude/                       # 레포 전용 스킬
│   └── frontend/
│
└── data/                                  # 런타임 데이터
    ├── tasks/                             # Task 포인터 + worktree (gitignore)
    │   └── payment-feature/
    │       ├── CLAUDE.md
    │       ├── TASK.md                    # vault 경로 포인터
    │       └── subtasks/
    └── history/                           # 완료된 Task 요약
```

### 로딩 우선순위

Claude Code는 다음 순서로 자동 discovery 합니다:

```
1. 플러그인 (~/.claude/plugins/cache/workbench-local/)  # Core
2. Personal (~/.claude/)                                 # 개인 글로벌
3. Project (.claude/)                                    # Workspace/Repo
```

### 레이어별 역할

| 레이어 | 위치 | 역할 | 예시 |
|--------|------|------|------|
| **Core** | `~/.claude/plugins/cache/workbench-local/` | 공통 기능 | `/wb-start`, `/wb-done` |
| **Workspace** | `.claude/` | 팀/회사별 커스텀 | `/zb-deploy`, 코딩컨벤션 |
| **Repo** | `repos/{repo}/.claude/` | 레포 특화 | `/api-test`, API 패턴 |
| **Task** | `data/tasks/{task}/` | Task별 컨텍스트 | CLAUDE.md, TASK.md |

### Workspace 커스터마이징

Workspace `.claude/` 폴더에 추가하면 Core와 함께 사용됩니다 (오버라이드 아님, 확장):

**스킬/커맨드 추가:**
```
.claude/skills/zb-deploy/SKILL.md      # 커스텀 커맨드
.claude/skills/zb-api-patterns/SKILL.md # API 컨벤션
```

**에이전트 추가:**
```
.claude/agents/zb-reviewer.md    # 커스텀 코드리뷰어
```

---

## 스킬 목록

### 커맨드 스킬 (사용자 호출)

| 스킬 | 설명 |
|------|------|
| `wb` | 도움말 표시 |
| `wb-init` | Workspace 초기화 |
| `wb-start` | Task 시작 |
| `wb-plan` | PRD 기반 작업 계획 수립 |
| `wb-save` | 중간 저장 |
| `wb-check` | 설계-구현 검증 |
| `wb-done` | 서브태스크 완료 |
| `wb-pr` | PR 생성 |
| `wb-next` | 다음 서브태스크 |
| `wb-run` | 독립 서브태스크 병렬 실행 |
| `wb-resume` | 컨텍스트 복원 |
| `wb-end` | Task 완료 |
| `wb-status` | 상태 조회 |
| `wb-update` | 플러그인 마이그레이션 |
| `wb-add-repo` | 레포 등록 |
| `wb-add-subtask` | 서브태스크 추가 |
| `wb-memo` | AI Memory에 메모 저장 |
| `wb-recall` | AI Memory에서 검색 |
| `wb-refresh` | 프론트로딩 갱신 (Vault 변경 반영) |
| `wb-save-skill` | 패턴을 Skill로 저장 |

### 인프라 스킬 (내부 사용)

| 스킬 | 설명 |
|------|------|
| `vault-conventions` | Obsidian vault PARA 규칙 및 SUBTASK.md 최소 템플릿 |
| `obsidian-vault-audit` | Vault PARA 구조 건강 진단 |
| `code-analysis` | 코드 분석 도구 |
| `branch-rules` | 브랜치 명명 규칙 |
| `decision-logger` | 의사결정 자동 기록 |
| `knowledge-extract` | 완료 Task에서 지식 추출 |
| `subtask-analyzer` | 서브태스크 분석 및 작업지시서 생성 |
| `worktree-guard` | repos/ 직접 수정 방지 |
| `skill-authoring-guide` | 스킬 작성 가이드 |
| `weekly-review` | 주간 리뷰 생성 |

### 에이전트

| 에이전트 | 모델 | 용도 |
|----------|------|------|
| analyzer | opus | Task 분석, 영향도 분석 |
| checker | opus | 분석 결과 검증, 일관성 체크 |
| implementer | sonnet | 코드 구현, 리팩토링 |
| reviewer | haiku | 코드 리뷰, 빠른 검증 |
| tester | sonnet | 테스트 작성, 실행 |

---

## 훅 (Hooks)

Workbench 플러그인은 `hooks.json`을 통해 Core 훅을 정의합니다.

### Core 훅

| 훅 | 파일 | 트리거 | 역할 |
|----|------|--------|------|
| **SessionStart** | `session-start.js` | 세션 시작 시 | Workspace 정보 수집, 배너 출력, Task 상태 복원 |
| **PostToolUse** | `detect-decision.sh` | Edit/Write 후 | 코드 변경에서 의사결정 패턴 감지 |
| **Stop** | `auto-save.sh` | 세션 종료 시 | 진행 중 Task 상태 자동 저장 |

### Workspace 훅 추가

`.claude/settings.local.json`에서 Workspace 단위 훅을 추가할 수 있습니다:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "bash .claude/hooks/my-custom-hook.sh"
        }]
      }
    ]
  }
}
```

---

## 사용 예시

### Day 1: Task 시작

```bash
cd ~/Workspaces/work
claude

> /wb-start "결제 기능"

🎯 목표를 알려주세요.
> Stripe로 카드 결제 구현

📋 서브태스크 초안:
1. [ ] PG 연동 (backend)
2. [ ] 결제 UI (frontend)
3. [ ] 통합 테스트 (backend, frontend)

확정하시겠습니까? (Y/n)
> Y

✅ Task 시작: payment-feature
📋 첫 서브태스크: PG 연동
🌿 브랜치: feature/payment/pg-integration
```

### Day 1: 작업 & 완료

```bash
# 작업 진행...

> /wb-done

📝 완료한 작업:
> PG 모듈 구현, webhook 핸들러 추가

💡 중요한 결정이 있었나요?
> webhook 타임아웃 30초로 설정

✅ 서브태스크 완료: PG 연동

> /wb-pr

✅ PR #123 생성됨
```

### Day 2: 이어서 작업

```bash
> /wb-resume

📋 Task: 결제 기능
✅ 1. PG 연동 (PR #123)
⬜ 2. 결제 UI ← 현재
⬜ 3. 통합 테스트

📅 어제: PG 연동 완료, webhook 30초 타임아웃

> /wb-next

✅ 서브태스크 시작: 결제 UI
🌿 브랜치: feature/payment/payment-ui
```

### Day 3: Task 완료

```bash
> /wb-end

📊 Task 완료: 결제 기능
- 서브태스크: 3개
- PR: #123, #124, #125

💾 AI Memory에 저장됨:
- webhook 타임아웃 설정
- Stripe 연동 패턴

💡 Skill로 저장할까요?
> /wb-save-skill "pg-integration"

✅ .claude/skills/pg-integration/SKILL.md 생성됨
```

---

## Workspace Sample

`workspace-sample/` 폴더에 예시 Workspace가 포함되어 있습니다.

```bash
cp -r workspace-sample ~/Workspaces/my-project
cd ~/Workspaces/my-project
git init
# config.json, repos.json 수정 후
claude  # → /wb-start로 시작
```

포함된 내용:
- `config.json` — Workspace 기본 설정
- `repos.json` — 레포 등록 예시
- `.claude/skills/` — 예시 Workspace 스킬
- `obsidian/` — PARA vault 디렉토리 구조
- `CLAUDE.md` — Workspace 설명 템플릿

> 상세한 커스터마이징은 README의 "Workspace 구조" 섹션을 참조하세요.

---

## 버전 히스토리

| 버전 | 주요 변경 |
|------|----------|
| v2.0.0 | **SUBTASK.md 가드레일** — 누락 방지, 공통 템플릿, 원자적 생성 |
| v1.9.0 | Session Start Vault SSoT, wb-update 캐시 수정 |
| v1.8.3 | wb-run 배치 PR, wb-end 히스토리 폴더 정리 |
| v1.8.2 | wb-refresh 스킬, FTS5 schema v4 |
| v1.8.1 | wb-save-skill agentskills.io 표준 |
| v1.8.0 | 한국어 FTS5 토크나이저 (kiwipiepy), UNINDEXED 컬럼 |
| v1.7.0 | wb-update 원스톱 업데이트 — 소스 pull + 캐시 동기화 통합 |
| v1.6.0 | FTS5 Vault 인덱서 (Beta), 토큰 소모 ~88% 절감 |
| v1.5.0 | 컨텍스트 최적화 — 어댑터 레이어 제거, 프론트로딩 도입 |
| v1.4.1 | obsidian-vault-audit 스킬 추가 (PARA vault 건강 진단) |
| v1.4.0 | Obsidian PARA vault 통합, 어댑터 추상화 완성 |
| v1.3.0 | 어댑터 인터페이스 도입 (task-manager, memory-manager) |
| v1.2.0 | Claude Code 플러그인 아키텍처로 전환 |
| v1.1.0 | 초기 릴리스 |

마이그레이션 가이드는 `migrations/` 폴더를 참조하세요.

---

## 기여

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 설계-구현 검증 (wb-check)

code 유형 서브태스크는 `/wb-done` 전에 자동으로 설계-구현 일치도를 검증합니다.

| Match Rate | 판정 | 다음 단계 |
|-----------|------|----------|
| >= 90% | ✅ 통과 | /wb-done 진행 |
| 70-89% | ⚠️ 수정 권장 | Gap 해결 후 재검증 |
| < 70% | ❌ 재작업 | 설계 재검토 |

## Skills 버전 정책

| 변경 유형 | 버전 | 예시 |
|----------|------|------|
| 기능 추가 (호환) | minor | wb-done에 옵션 추가 |
| Breaking change | major | 명령어 시그니처 변경 |
| 버그 수정/문서 | patch | 설명 수정 |

## Release 체크리스트

code 유형 `/wb-done` 시 자동 검증:
- 코드 품질: lint, type-check, build
- 테스트: 회귀 없음, 신규 커버리지 >= 80%
- 커밋: Conventional Commits, 민감정보 미포함
- 문서: README/마이그레이션/버전 범프 확인

---

## 라이선스

MIT License - see [LICENSE](LICENSE) for details.
