# Workspace Sample

Workbench 플러그인을 사용하기 위한 예시 Workspace입니다.

## 사용법

```bash
# 1. 이 폴더를 원하는 위치에 복사
cp -r workspace-sample ~/Workspaces/my-project
cd ~/Workspaces/my-project
git init

# 2. config.json에서 이름 수정
# 3. repos.json에 레포 등록
# 4. Claude Code 실행
claude

# 5. Task 시작
> /wb-start "첫 번째 Task"
```

## 구조

```
workspace-sample/
├── CLAUDE.md                    # Workspace 설명
├── config.json                  # 기본 설정
├── repos.json                   # 레포 목록 (예시 포함)
├── .gitignore                   # repos/, data/ 제외
│
├── .claude/
│   ├── settings.local.json      # 훅 설정
│   └── skills/                  # Workspace 스킬
│       ├── coding-conventions/  # 코딩 컨벤션
│       └── repos-guide/         # 레포별 개발 가이드
│           ├── SKILL.md         # 인덱스
│           └── references/      # 레포별 상세
│               ├── backend.md
│               └── frontend.md
│
└── obsidian/                    # Obsidian vault (PARA)
    ├── 1-Projects/              # 활성 Task
    │   └── example-task/        # Task 예시
    ├── 2-Areas/                 # 도메인 지식
    │   ├── domains/             # 비즈니스 도메인별 정리
    │   │   ├── users.md         # 사용자/인증 도메인
    │   │   ├── products.md      # 상품 도메인
    │   │   └── payments.md      # 결제 도메인
    │   └── development-process.md
    ├── 3-Resources/             # AI Memory (재사용 지식)
    │   ├── patterns/            # 코드 패턴
    │   ├── guides/              # 작업 가이드
    │   └── troubleshooting/     # 트러블슈팅 기록
    └── 4-Archives/              # 완료된 Task
```

## Vault 지식 체계

Obsidian vault는 **PARA** 구조로 지식을 관리합니다.

### 1-Projects: 활성 Task
현재 진행 중인 Task가 위치합니다. `/wb-start`로 자동 생성되고 `/wb-end`로 4-Archives로 이동합니다.

### 2-Areas: 도메인 지식
**비즈니스 도메인별로 분리**된 영구 지식입니다. 팀의 도메인 이해를 문서화합니다.

```
2-Areas/domains/
├── users.md       # 인증 플로우, 역할, 비즈니스 규칙
├── products.md    # 상품 상태 머신, 카테고리, 검색
└── payments.md    # 결제 상태, PG 연동, 환불 정책
```

AI가 Task 시작 시 관련 도메인 문서를 자동 검색하여 컨텍스트로 제공합니다.

### 3-Resources: AI Memory
작업 중 축적되는 재사용 지식입니다. `/wb-memo`로 저장하고 `/wb-recall`로 검색합니다.

| 카테고리 | 예시 |
|---------|------|
| patterns/ | API 에러 핸들링, 상태 관리 패턴 |
| guides/ | Git worktree 가이드, 배포 절차 |
| troubleshooting/ | Docker 메모리 이슈, CI 실패 대응 |

### 4-Archives: 완료된 Task
`/wb-end`로 완료된 Task가 자동 보관됩니다. 의사결정 기록과 요약이 보존됩니다.

## 커스터마이징

- `config.json`: Workspace 이름, vault 경로, 기본 브랜치 설정
- `repos.json`: 작업할 레포 등록 (`/wb-add-repo`로도 가능)
- `.claude/skills/`: Workspace 전용 스킬 추가
- `.claude/agents/`: Workspace 전용 에이전트 추가
- `obsidian/2-Areas/domains/`: 팀 도메인 문서 추가
