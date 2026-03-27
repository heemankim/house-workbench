# Workbench Workspace: {{WORKSPACE_NAME}}

{{DESCRIPTION}}

---

## 🛠️ Workspace Loaded

```
┌────────────────────────────────────────────────────────────┐
│  🏠 Workspace: {{WORKSPACE_NAME}}                           │
│  ─────────────────────────────────────────────────────────  │
│                                                            │
│  📦 Adapters:                                              │
│  ├─ Task Manager: {{TASK_MANAGER}}                         │
│  └─ AI Memory: {{AI_MEMORY}}                               │
│                                                            │
│  📚 Skills ({{SKILL_COUNT}}):                               │
│  {{SKILL_LIST}}                                            │
│                                                            │
│  🤖 Agents:                                                │
│  ├─ analyzer (opus) - 분석/설계                             │
│  ├─ checker (opus) - 검증                                  │
│  ├─ implementer (sonnet) - 구현                            │
│  ├─ tester (sonnet) - 테스트                               │
│  └─ reviewer (haiku) - 리뷰                                │
│                                                            │
│  📂 Repos ({{REPO_COUNT}}):                                 │
│  {{REPO_LIST}}                                             │
│                                                            │
│  🪝 Hooks: PostToolUse, Stop                               │
│                                                            │
│  ─────────────────────────────────────────────────────────  │
│  /wb - 도움말 | /wb-status - 상태 | /wb-start - 시작        │
└────────────────────────────────────────────────────────────┘
```

---

## 명령어

### Core (wb-*)
| 명령어 | 설명 |
|--------|------|
| `/wb-start` | Task 시작 |
| `/wb-resume` | 이어서 작업 |
| `/wb-done` | 서브태스크 완료 |
| `/wb-next` | 다음 서브태스크 |
| `/wb-end` | Task 종료 |
| `/wb-status` | 상태 조회 |

### Workspace 전용
{{WORKSPACE_COMMANDS}}

## Agents

| Agent | Model | 용도 |
|-------|-------|------|
| `analyzer` | opus | 복잡한 분석, 영향도 파악, 설계 |
| `checker` | opus | 분석 결과 검증, 일관성 체크 |
| `implementer` | sonnet | 코드 구현, 리팩토링 |
| `tester` | sonnet | 테스트 작성 및 실행 |
| `reviewer` | haiku | 빠른 코드 리뷰 |

## Skills

{{SKILLS_DETAIL}}

## Repos

{{REPOS_DETAIL}}

## 구조

```
{{WORKSPACE_PATH}}/
├── .claude/          → workbench-core (submodule)
├── commands/         # Workspace 전용 명령어
├── .claude/skills/   # Workspace 지식
├── config.json       # 어댑터 설정
├── repos.json        # 레포 목록
├── repos/            # 원본 레포
└── tasks/            # Task들
```

## 활용 내역

세션 중 사용된 리소스는 다음 형식으로 표시됩니다:

```
📊 커맨드/작업 실행 완료
├─ 🤖 Agents: {사용된 에이전트}
├─ 💾 Memory: {메모리 작업}
├─ 📚 Skills: {참조된 스킬}
├─ 🔧 Actions: {수행된 작업}
└─ ⏱️ 소요: {시간}
```
