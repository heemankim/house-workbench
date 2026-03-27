---
name: coding-conventions
description: Team coding conventions and style guide. Reference when writing or reviewing code.
metadata:
  author: workspace
  version: "1.0.0"
---

# coding-conventions: 코딩 컨벤션

팀 코딩 컨벤션 가이드입니다. 코드 작성 및 리뷰 시 참조합니다.

## TypeScript

- strict mode 사용
- interface > type alias (확장 가능한 경우)
- enum 대신 const object + as const 사용

## 네이밍

| 대상 | 규칙 | 예시 |
|------|------|------|
| 변수/함수 | camelCase | `getUserById` |
| 클래스/인터페이스 | PascalCase | `UserService` |
| 상수 | UPPER_SNAKE | `MAX_RETRY_COUNT` |
| 파일 | kebab-case | `user-service.ts` |

## Git 커밋

Conventional Commits:
- `feat:` 새 기능
- `fix:` 버그 수정
- `refactor:` 리팩토링
- `docs:` 문서
- `test:` 테스트

## 테스트

- 단위 테스트: `*.spec.ts`
- 통합 테스트: `*.integration.spec.ts`
- 커버리지 목표: 80%
