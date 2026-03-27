---
name: worktree-guard
description: Prevents direct modification of files in the repos/ directory and guides users to worktrees. Use as a safety guard to enforce worktree-based workflow.
metadata:
  author: workbench
  version: "1.5.0"
---

# worktree-guard: repos/ 직접 수정 방지

`repos/` 디렉토리의 코드를 직접 수정하려는 시도를 감지하고, worktree를 통한 작업을 안내합니다.

## 규칙

**`repos/` 하위 파일은 직접 수정하지 않습니다.**

코드 변경은 반드시 worktree에서 수행합니다:
```
repos/{repo}/          ← 원본. 직접 수정 금지
data/tasks/{task}/subtasks/{nn}-xxx/{repo}/{branch}/  ← worktree. 여기서 작업
```

## 감지 조건

다음 경로에 대한 Edit/Write 시도 시 안내를 표시합니다:

```
repos/{repo}/src/**
repos/{repo}/lib/**
repos/{repo}/app/**
repos/{repo}/test/**
repos/{repo}/**/*.{js,ts,py,rb,go,java,rs,md,json,yaml,yml}
```

**예외 (직접 수정 허용):**
- `repos/{repo}/.claude/` — 레포 스킬/설정
- `repos/{repo}/CLAUDE.md` — 레포 지침
- `/wb-add-repo` 실행 중 초기 설정

## 안내 메시지

### Task가 진행 중인 경우

```
⚠️ repos/{repo}/ 직접 수정은 권장하지 않습니다.

현재 Task: {task-name}
현재 서브태스크: {subtask-name}

worktree 경로:
  data/tasks/{task-name}/subtasks/{nn}-{subtask-name}/{repo}/{branch}/

이 경로에서 작업하시겠습니까? (Y/n)
```

`Y` 선택 시:
1. worktree 경로로 이동하여 동일 파일 수정
2. 변경 사항이 올바른 브랜치에 기록됨

### Task가 없는 경우

```
⚠️ repos/{repo}/ 직접 수정은 권장하지 않습니다.

진행 중인 Task가 없습니다.
코드 변경은 Task를 시작한 후 worktree에서 작업하세요.

시작하기:
  /wb-start "{task-name}" → Task 생성 + worktree 자동 생성

간단한 확인/읽기만 하는 경우라면 그대로 진행합니다.
```

### worktree가 아직 생성되지 않은 경우

```
⚠️ repos/{repo}/ 직접 수정은 권장하지 않습니다.

현재 서브태스크의 worktree가 아직 없습니다.
/wb-next로 다음 서브태스크를 시작하면 worktree가 자동 생성됩니다.

지금 생성하시겠습니까? (Y/n)
```

`Y` 선택 시:
```bash
cd repos/{repo}
git pull origin {baseBranch}
git worktree add ../../data/tasks/{task}/subtasks/{nn}-{subtask}/{repo}/{branch} -b {branch}
```

## 읽기 전용 접근

`repos/`에서 **읽기**는 자유롭게 허용됩니다:
- 코드 구조 파악
- 참조 검색
- 의존성 확인

수정만 worktree로 유도합니다.
