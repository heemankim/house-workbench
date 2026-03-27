---
tags: [domain, products, catalog]
---

# 상품 도메인

## TL;DR
상품 카탈로그 CRUD, 카테고리 트리, 재고 관리. 검색은 Elasticsearch 연동.

## 핵심 개념

```
판매자 → 상품 등록 → 검수 → 노출
                      ↓
                 카테고리 배치 + 검색 인덱싱
```

## 상품 상태

```
DRAFT → PENDING_REVIEW → ACTIVE → SOLD_OUT
  ↓         ↓              ↓
REJECTED  SUSPENDED      DELETED
```

## 카테고리 구조

```
전자기기
├── 스마트폰
│   ├── iOS
│   └── Android
├── 노트북
└── 태블릿
```

- 최대 3단계 depth
- 상품은 리프 카테고리에만 등록 가능

## 비즈니스 규칙

- 상품명: 2~100자
- 가격: 100원 이상
- 이미지: 최소 1장, 최대 10장
- 재고 0 → 자동 SOLD_OUT 전이
- 검색 인덱스: 상품 변경 후 최대 5분 내 반영

## 관련 코드

- `backend/src/modules/products/` — 상품 모듈
- `backend/src/modules/categories/` — 카테고리 모듈
- `frontend/src/pages/products/` — 상품 목록/상세 페이지
