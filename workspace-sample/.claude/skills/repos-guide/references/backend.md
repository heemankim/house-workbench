# Backend 레포 가이드

## 개요
- 프레임워크: NestJS
- DB: PostgreSQL + TypeORM
- 패키지 매니저: pnpm

## 빌드 & 실행

```bash
pnpm install
pnpm run build
pnpm run start:dev
```

## 테스트

```bash
# 단위 테스트
pnpm run test

# 통합 테스트 (DB 필요)
pnpm run test:e2e

# 커버리지
pnpm run test:cov
```

## DB 마이그레이션

```bash
# 마이그레이션 생성
pnpm run migration:generate -- -n MigrationName

# 마이그레이션 실행
pnpm run migration:run

# 마이그레이션 롤백
pnpm run migration:revert
```

## 환경변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `DATABASE_URL` | DB 연결 | `postgresql://user:pass@localhost:5432/db` |
| `PORT` | 서버 포트 | `3000` |
| `NODE_ENV` | 실행 환경 | `development` |

## 디렉토리 구조

```
src/
├── modules/          # 도메인별 모듈
│   ├── auth/
│   ├── users/
│   └── payments/
├── common/           # 공통 유틸
├── config/           # 설정
└── main.ts
```

## Worktree 작업 시 주의

- `node_modules/`는 worktree별로 별도 설치 필요 (`pnpm install`)
- `.env` 파일은 worktree에 자동 복사 안 됨 — 수동 복사 또는 심링크
