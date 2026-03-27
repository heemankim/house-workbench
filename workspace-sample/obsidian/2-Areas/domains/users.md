---
tags: [domain, users, auth]
---

# 사용자 도메인

## TL;DR
JWT 기반 인증, 회원가입/로그인/탈퇴 플로우. 역할(Role) 기반 권한 관리.

## 핵심 개념

```
회원가입 → 이메일 인증 → 로그인 (JWT) → 서비스 이용
                                         ↓
                                    토큰 갱신 (Refresh)
```

## 사용자 역할

| 역할 | 설명 | 권한 |
|------|------|------|
| USER | 일반 사용자 | 조회, 주문, 프로필 수정 |
| SELLER | 판매자 | + 상품 등록, 주문 관리 |
| ADMIN | 관리자 | + 사용자 관리, 통계 |

## 인증 플로우

```
1. 로그인 → accessToken (15분) + refreshToken (7일)
2. API 요청 → Authorization: Bearer {accessToken}
3. 만료 시 → refreshToken으로 갱신
4. refreshToken 만료 → 재로그인
```

## 비즈니스 규칙

- 비밀번호: 8자 이상, 영문+숫자+특수문자
- 로그인 실패 5회 → 30분 잠금
- 탈퇴 시 개인정보 30일 보관 후 삭제 (법적 요건)
- 이메일 변경 시 재인증 필수

## 관련 코드

- `backend/src/modules/auth/` — 인증 모듈
- `backend/src/modules/users/` — 사용자 CRUD
- `backend/src/common/guards/roles.guard.ts` — 역할 가드
