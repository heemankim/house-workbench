# Workbench

AI 에이전트 작업을 위한 컨텍스트 관리 프레임워크

---

## 🛠️ Workbench Core Loaded

```
┌────────────────────────────────────────────────────────────┐
│  Workbench v2.1.0                                          │
│                                                            │
│  📚 Skills:                                                │
│  ├─ vault-conventions Vault PARA 규칙 + SUBTASK.md 템플릿   │
│  ├─ subtask-analyzer  서브태스크 분석                       │
│  ├─ code-analysis     Serena 코드 분석                     │
│  └─ worktree-guard    repos/ 직접 수정 방지                 │
│                                                            │
│  🤖 Agents:                                                │
│  ├─ analyzer          분석 (opus)                          │
│  ├─ checker           검증 (opus)                          │
│  ├─ implementer       구현 (sonnet)                        │
│  ├─ reviewer          리뷰 (haiku)                         │
│  └─ tester            테스트 (sonnet)                      │
│                                                            │
│  🪝 Hooks:                                                 │
│  ├─ detect-decision   의사결정 감지 → AI Memory            │
│  └─ auto-save         세션 종료 시 자동 저장                │
│                                                            │
│  💡 /wb - 도움말 | /wb-status - 상태                       │
└────────────────────────────────────────────────────────────┘
```

**Note**: Workspace 레벨의 skills, commands, repos는 상위 폴더에서 로드됩니다.

---

## 항상 활성 규칙

### repos/ 직접 수정 금지

`repos/` 하위 코드 파일을 직접 수정하지 않습니다. 코드 변경은 반드시 worktree에서 수행합니다.
상세: `skills/worktree-guard/SKILL.md` 참조

---

## 명령어

### 초기화
| 명령어 | 설명 |
|--------|------|
| `/wb-init` | Workspace 초기화 |
| `/wb-add-repo` | 레포 등록 |

### Task 라이프사이클
| 명령어 | 설명 |
|--------|------|
| `/wb` | 헬퍼 (도움말) |
| `/wb-start` | Task 시작, 서브태스크 초안 |
| `/wb-plan` | PRD 기반 작업 계획 수립 |
| `/wb-check` | 설계-구현 검증 |
| `/wb-run` | 독립 서브태스크 병렬 실행 |
| `/wb-resume` | 이어서 작업 (컨텍스트 복원) |
| `/wb-refresh` | 프론트로딩 갱신 |
| `/wb-save` | 중간 저장 |
| `/wb-done` | 서브태스크 완료 |
| `/wb-next` | 다음 서브태스크로 |
| `/wb-end` | Task 전체 완료 |
| `/wb-status` | 상태 조회 |

### 지식 관리
| 명령어 | 설명 |
|--------|------|
| `/wb-memo` | AI Memory에 메모 저장 |
| `/wb-recall` | AI Memory에서 검색 |
| `/wb-add-subtask` | 서브태스크 추가 |
| `/wb-save-skill` | 지식을 Skill로 저장 |
| `/wb-pr` | PR 생성 |

---

## 출력 형식

### 명령어 실행 후 활용 내역

각 wb-* 명령어 실행 후 다음 형식으로 활용 내역을 표시하세요:

```
🛠️ Workbench: /wb-start "결제 기능"

📚 Context Loaded:
├─ Skill: task-manager → Todoist 프로젝트 조회
├─ Skill: memory-manager → 관련 기억 3개 검색
├─ Skill: repo-backend → 레포 정보 로드
└─ Agent: analyzer (opus) → 서브태스크 분석

💾 State Updated:
├─ Task 생성: payment-feature
├─ 서브태스크: 3개 계획됨
└─ AI Memory: Task 시작 기록

✅ 완료: Task 시작됨

다음 단계:
1. 작업을 진행하세요
2. /wb-done으로 서브태스크 완료
```

### 간단한 명령어의 경우

```
🛠️ Workbench: /wb-status

📋 결과 표시...

✅ 완료
```

---

## Agents

| Agent | 모델 | 용도 |
|-------|------|------|
| analyzer | opus | Task 분석, 영향도 분석, 의존성 분석 |
| checker | opus | 분석 결과 검증, 일관성 체크 |
| implementer | sonnet | 코드 구현, 리팩토링 |
| reviewer | haiku | 코드 리뷰, 빠른 검증 |
| tester | sonnet | 테스트 작성, 실행 |

**모델 선택 기준:**
- `opus`: 복잡한 분석, 중요한 결정
- `sonnet`: 일반 구현, 균형잡힌 작업
- `haiku`: 빠른 검증, 간단한 작업

---

## 계층 구조

```
Core (.claude/ 서브모듈)
└── Workspace
    ├── .claude/skills/ ← Workspace 지식 (모든 Task 공유)
    ├── commands/      ← Workspace 전용 명령어
    └── tasks/
        └── Task
            ├── CLAUDE.md    ← 레포 skills 참조
            ├── TASK.md      ← 작업지시서
            └── subtasks/
```

## 지식 계층

```
세션 내 (휘발)     → 현재 대화
Task 내 (파일)     → TASK.md, history/
Task 간 (Memory)   → AI Memory
영구 (Skills)      → .claude/skills/*.md
```

## 우선순위

```
1. tasks/{task}/           ← Task 레벨
2. ~/Workspaces/{name}/    ← Workspace 레벨
3. .claude/ (Core)         ← 기본값
```
