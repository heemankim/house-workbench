---
name: wb-add-repo
description: Registers a new repository to the workspace with code analysis. Use when adding a git repository to be managed by Workbench.
metadata:
  author: workbench
  version: "1.5.0"
  skills:
    - code-analysis
---

# wb-add-repo: 레포 추가

Workspace에 새 레포를 등록합니다.

## 입력
- `$ARGUMENTS`: 레포 이름 또는 URL (선택)

## 프로세스

### 1. 레포 정보 수집

```
📦 레포 추가

이름 (폴더명으로 사용):
> backend

원격 URL:
> git@github.com:company/backend.git

기본 베이스 브랜치 (main):
> develop

브랜치 접두사 (feature/):
> feature/
```

### 2. repos.json 업데이트

```json
{
  "repos": [
    {
      "name": "backend",
      "remote": "git@github.com:company/backend.git",
      "defaultBase": "develop",
      "branchPrefix": "feature/"
    }
  ]
}
```

### 3. 클론 여부 확인

```
📥 레포를 클론할까요? (Y/n)
> y

cd repos && git clone git@github.com:company/backend.git
```

### 3.5. Serena 프로젝트 온보딩 (자동)

`skills/code-analysis/SKILL.md`의 **프로젝트 활성화** 프로시저를 실행합니다.
대상: `repos/{repo-name}`

```
🧠 Serena 온보딩 완료: backend
   → 프로젝트 구조 분석됨
   → 이후 /wb-plan, /wb-start에서 심볼릭 코드 탐색 가능
```

비활성화 또는 Serena MCP 미설치 시 → 스킵

### 4. 레포 .claude 감지

```
💡 레포에 .claude 폴더가 있습니다:
- skills/api-patterns/SKILL.md
- skills/test-guide/SKILL.md

이 레포 작업 시 자동으로 참조됩니다.
```

### 5. Workspace skill 생성 제안

```
📝 레포 정보를 skill로 저장할까요? (Y/n)
> y

.claude/skills/repo-backend/SKILL.md 생성됨
→ /repo-backend로 호출 가능
```

### 6. 완료 메시지

```
✅ 레포 추가됨: backend

📦 등록된 레포: 2개
- backend (develop)
- frontend (develop)

/wb-start 시 선택 가능합니다.
```
