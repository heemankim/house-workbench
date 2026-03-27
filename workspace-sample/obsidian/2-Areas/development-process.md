---
tags: [process, development, team]
---

# 개발 프로세스

## TL;DR
기획 → 설계 → 구현(Workbench Task) → 코드리뷰 → QA → 배포. Task는 서브태스크 = PR 단위로 분리.

## 워크플로우

```
1. 기획서/PRD 작성
   ↓
2. /wb-plan으로 서브태스크 분해
   ↓
3. /wb-start로 Task 시작
   ↓
4. 서브태스크별 구현
   ├── /wb-done → /wb-pr (코드 리뷰)
   └── /wb-next (다음 서브태스크)
   ↓
5. QA 승인
   ↓
6. 배포
   ↓
7. /wb-end (Task 완료 + 지식 축적)
```

## 브랜치 전략

```
main
├── feature/{task}/{subtask-1}  → PR #1
├── feature/{task}/{subtask-2}  → PR #2
└── feature/{task}/{subtask-3}  → PR #3
```

## 리뷰 기준

- PR 크기: 서브태스크 단위 (리뷰 가능한 크기)
- 테스트 커버리지: 80% 이상
- Conventional Commits 준수
