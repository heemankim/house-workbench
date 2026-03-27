---
name: repos-guide
description: Repository-specific development guides. Reference when working with each repo for build, test, and deployment procedures.
metadata:
  author: workspace
  version: "1.0.0"
---

# repos-guide: 레포별 개발 가이드

멀티레포 환경에서 각 레포의 빌드, 테스트, 배포 절차를 참조합니다.

## 레포 목록

| 레포 | 주요 내용 | 가이드 |
|------|----------|--------|
| backend | NestJS API, DB 마이그레이션, 테스트 | [상세](references/backend.md) |
| frontend | React SPA, 빌드, Storybook | [상세](references/frontend.md) |

## 새 레포 추가 시

1. `references/{repo-name}.md` 파일 생성
2. 위 테이블에 행 추가
3. `/wb-add-repo`로 repos.json에 등록
