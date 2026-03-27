---
tags: [git, worktree, workflow]
---

# Git Worktree 작업 가이드

## TL;DR
멀티레포 환경에서 서브태스크별 독립 브랜치를 worktree로 관리. 원본 레포는 항상 깨끗하게 유지.

## 기본 흐름

```
repos/backend/          ← 원본 (main, 항상 최신)
    ↓ git worktree add
data/tasks/{task}/subtasks/01/backend/{branch}/  ← 작업용
```

## 핵심 명령어

```bash
# worktree 생성
git worktree add ../../data/tasks/my-task/subtasks/01/backend/feature-branch -b feature-branch

# worktree 목록 확인
git worktree list

# worktree 제거 (브랜치는 유지)
git worktree remove data/tasks/my-task/subtasks/01/backend/feature-branch
```

## 주의사항

- 같은 브랜치를 두 worktree에서 체크아웃 불가
- `node_modules/`는 worktree마다 별도 설치 필요
- `.env` 파일은 자동 복사 안 됨 (수동 복사 또는 심링크)
- worktree 정리 전 미커밋 변경사항 확인
