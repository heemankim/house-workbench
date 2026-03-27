---
tags: [domain, payments, business-rules]
---

# 결제 도메인

## TL;DR
PG사 연동 기반 카드/계좌이체 결제. 결제 상태 머신 관리, webhook 비동기 처리, 환불/취소 정책.

## 핵심 개념

```
사용자 → 결제 요청 → PG사 → webhook → 결제 확정
                              ↓
                        결제 상태 머신
```

## 상태 머신

```
PENDING → APPROVED → COMPLETED
  ↓         ↓          ↓
FAILED   CANCELLED   REFUNDED
```

| 상태 | 설명 | 전이 가능 |
|------|------|----------|
| PENDING | 결제 요청됨 | APPROVED, FAILED |
| APPROVED | PG 승인 | COMPLETED, CANCELLED |
| COMPLETED | 결제 완료 | REFUNDED |
| FAILED | 결제 실패 | (종료) |
| CANCELLED | 결제 취소 | (종료) |
| REFUNDED | 환불 완료 | (종료) |

## 비즈니스 규칙

- 최소 결제 금액: 100원
- 환불 기한: 결제 후 7일 이내
- 부분 환불: 1회만 허용
- PG webhook 타임아웃: 30초
- 결제 중복 방지: idempotency key 필수

## 관련 코드

- `backend/src/modules/payments/` — 결제 모듈
- `backend/src/modules/payments/entities/payment.entity.ts` — 결제 엔티티
- `backend/src/modules/payments/payment-state-machine.ts` — 상태 머신

## 관련 문서

- [[api-error-handling]] — 결제 실패 시 에러 응답 패턴
