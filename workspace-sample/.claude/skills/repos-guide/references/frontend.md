# Frontend 레포 가이드

## 개요
- 프레임워크: React + TypeScript
- 빌드: Vite
- 상태관리: Zustand
- 스타일: Tailwind CSS

## 빌드 & 실행

```bash
pnpm install
pnpm run dev        # 개발 서버 (localhost:5173)
pnpm run build      # 프로덕션 빌드
pnpm run preview    # 빌드 결과 미리보기
```

## 테스트

```bash
# 단위 테스트
pnpm run test

# 컴포넌트 테스트 (Storybook)
pnpm run storybook
```

## 디렉토리 구조

```
src/
├── components/       # UI 컴포넌트
│   ├── common/       # 공통 컴포넌트
│   └── features/     # 기능별 컴포넌트
├── hooks/            # 커스텀 훅
├── stores/           # Zustand 스토어
├── api/              # API 클라이언트
├── pages/            # 페이지 라우트
└── utils/            # 유틸리티
```

## API 연동

```typescript
// src/api/client.ts
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3000';
```

| 환경변수 | 설명 | 예시 |
|---------|------|------|
| `VITE_API_URL` | Backend API URL | `http://localhost:3000` |

## Worktree 작업 시 주의

- `node_modules/`는 worktree별로 별도 설치 필요
- `.env.local`은 자동 복사 안 됨
- Backend 레포와 함께 작업 시, 각각 별도 worktree에서 진행
