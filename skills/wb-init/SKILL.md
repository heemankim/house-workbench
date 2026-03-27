---
name: wb-init
description: Initializes a new Workbench workspace with default directory structure and configuration. Use when setting up a fresh workspace for the first time.
metadata:
  author: workbench
  version: "1.5.0"
---

# wb-init: Workspace 초기화

새 Workspace를 초기화합니다.

## 입력
- `$ARGUMENTS`: Workspace 이름 (선택, 기본값: 현재 폴더명)

## 프로세스

### 1. 현재 위치 확인

Workspace로 사용할 폴더인지 확인:
```
현재 폴더: ~/Workspaces/work
Workspace로 초기화할까요? (Y/n)
```

### 2. 기본 구조 생성

```bash
mkdir -p .claude/skills repos data/tasks data/history
```

### 3. config.json 생성

기본 config.json (obsidian vault 포함):
```json
{
  "name": "{workspace-name}",
  "vault": "obsidian",
  "pluginVersion": "{현재 플러그인 버전}",
  "defaults": {
    "baseBranch": "main",
    "branchPrefix": "feature/"
  },
  "beta": {}
}
```

> `beta` 블록은 실험적 기능의 opt-in 토글입니다.
> 사용 가능한 beta 기능: `fts-indexer` (Vault FTS5 검색, 기본값 false)

Obsidian vault를 기본으로 사용합니다.

```
Vault 경로 (기본: obsidian):
→ config.json에 "vault": "{경로}" 추가
→ PARA 폴더 구조 자동 생성 (0-Inbox, 1-Projects, 2-Areas, 3-Resources, 4-Archives, _templates)
```

> Task와 지식 모두 하나의 vault에서 통합 관리됩니다.

### 3.5. Obsidian Vault 초기화 (obsidian 선택 시)

Obsidian vault가 기본 백엔드입니다:

```bash
# PARA 폴더 구조 생성
mkdir -p {vault}/{0-Inbox,1-Projects,2-Areas,3-Resources/{patterns,troubleshooting,guides,references},4-Archives,_templates,daily,weekly}
```

> **0-Inbox**: 미분류 캡처 버퍼. Dashboard + 빠른 메모. 주간 리뷰 시 정리.
> **1-Projects**: 활성 태스크. wb-start가 자동 생성.
> **2-Areas**: 지속적 관리 영역 (회사, 개인 등). Area별 README.md로 기준 관리.
> **3-Resources**: 재사용 지식. patterns/, troubleshooting/, guides/, references/.
> **4-Archives**: 완료/취소된 태스크. wb-end/wb-cancel이 자동 이동.

기본 템플릿 파일 생성:
- `_templates/tpl-project.md` — 프로젝트 템플릿 (frontmatter + 서브태스크 인덱스 + wikilinks)
- `_templates/tpl-subtask.md` — 서브태스크 작업지시서 (분석, 체크리스트, 의사결정, 히스토리)
- `_templates/tpl-daily.md` — 데일리 노트 (Templater 구문)
- `_templates/tpl-weekly.md` — 주간 리뷰 (PARA 메인터넌스)
- `_templates/tpl-decision.md` — 의사결정 기록
- `_templates/tpl-resource.md` — 지식/리소스 노트
- `0-Inbox/Dashboard.md` — Dataview 대시보드 (Homepage 플러그인용)

Areas 하위 폴더 생성 여부:
```
기본 Areas를 생성할까요? (회사/개인 등)
> 폴더명을 입력하세요 (쉼표 구분, 예: work,personal):
```

```
✅ Obsidian vault 초기화 완료: {vault}/
├─ PARA 폴더: 0-Inbox, 1-Projects, 2-Areas, 3-Resources, 4-Archives
├─ 템플릿: 6개
└─ Dashboard: 0-Inbox/Dashboard.md

💡 Obsidian에서 {vault}/ 폴더를 vault로 열어주세요.
   추천 플러그인: Dataview, Templater, Tasks, Periodic Notes
```

### 4. repos.json 생성

```json
{
  "repos": []
}
```

레포 추가 여부:
```
📦 레포를 추가할까요? (y/N)
> y

레포 이름: backend
원격 URL: git@github.com:company/backend.git
기본 브랜치 (main): develop

더 추가? (y/N)
```

### 5. .gitignore 생성

```
repos/
data/tasks/
.env
.DS_Store
.idea/
.vscode/
# Obsidian (vault 자체는 포함, 기기별 설정은 제외)
obsidian/.obsidian/workspace.json
obsidian/.obsidian/workspace-mobile.json
```

### 6. CLAUDE.md 생성 (동적 배너 포함)

vault 경로와 레포 정보를 반영하여 생성:

```markdown
# Workbench Workspace: {name}

{description}

---

## 🛠️ Workspace Loaded

┌────────────────────────────────────────────────────┐
│  Workspace: {name}                                 │
│                                                    │
│  📦 Vault: {vault 경로}                            │
│                                                    │
│  📚 Skills: {개수}개                                │
│  📂 Repos: {개수}개                                 │
│                                                    │
│  /wb - 도움말 | /wb-status - 상태                   │
└────────────────────────────────────────────────────┘

---

## 명령어
...

## Skills
...

## Repos
...
```

### 7. settings.json 생성 (Hook 설정)

`.claude/settings.json` 생성:
```json
{
  "hooks": {
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

### 8. .claude 확인

`.claude/` 폴더가 없으면 생성:
```bash
mkdir -p .claude
```

`settings.json` 생성 (Hook 설정 등):
```
✅ .claude/settings.json 생성됨

💡 Workbench는 플러그인으로 설치됩니다.
   /plugins 에서 workbench 플러그인 상태를 확인하세요.
```

### 9. Git 초기화 (선택)

```
Git 초기화가 필요합니다.
git init을 실행할까요? (Y/n)
```

### 10. 완료 메시지 (활용 내역 포함)

```
🛠️ Workbench: /wb-init

📚 활용:
├─ Template: workspace/CLAUDE.md
├─ Template: workspace/config.json
├─ Template: workspace/settings.json
└─ Template: workspace/.gitignore

📁 생성됨:
├─ .claude/settings.json
├─ .claude/skills/
├─ config.json
├─ repos.json
├─ CLAUDE.md
├─ .gitignore
└─ obsidian/  (obsidian 어댑터 선택 시)

✅ Workspace 초기화 완료: {name}

다음 단계:
1. /wb-add-repo로 레포 등록
2. /wb-start로 Task 시작
```

## 이미 초기화된 경우

```
⚠️ 이미 Workspace가 초기화되어 있습니다.
config.json이 존재합니다.

재초기화할까요? (기존 설정 백업됨) (y/N)
```
