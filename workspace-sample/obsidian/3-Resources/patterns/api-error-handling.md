---
tags: [api, error-handling, pattern]
---

# API 에러 핸들링 패턴

## TL;DR
NestJS 글로벌 예외 필터 + 표준 에러 응답 포맷. 비즈니스 예외는 커스텀 Exception 클래스로 분리.

## 표준 에러 응답

```json
{
  "statusCode": 400,
  "error": "BAD_REQUEST",
  "message": "이메일 형식이 올바르지 않습니다",
  "timestamp": "2026-03-27T10:00:00Z"
}
```

## 예외 클래스 계층

```
HttpException (NestJS)
├── BusinessException (커스텀)
│   ├── UserNotFoundException
│   ├── DuplicateEmailException
│   └── InsufficientBalanceException
└── ValidationException (커스텀)
```

## 적용 방법

1. `GlobalExceptionFilter`로 모든 예외 캐치
2. `BusinessException` → 4xx 응답
3. 미처리 예외 → 500 + 로깅 (Sentry)
