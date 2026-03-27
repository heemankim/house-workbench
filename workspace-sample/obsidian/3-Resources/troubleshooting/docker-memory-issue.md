---
tags: [docker, memory, troubleshooting]
---

# Docker 메모리 부족 이슈

## TL;DR
로컬 Docker Desktop 메모리 4GB 기본값에서 Node.js 빌드 시 OOM 발생. 8GB로 증가 또는 `--max-old-space-size=4096` 설정.

## 증상
- `docker build` 중 프로세스 killed
- `FATAL ERROR: Reached heap limit Allocation failed`

## 해결

### 방법 1: Docker Desktop 메모리 증가
Settings → Resources → Memory → 8GB

### 방법 2: Node.js 힙 크기 지정
```dockerfile
ENV NODE_OPTIONS="--max-old-space-size=4096"
```

## 참고
- 발생일: 2026-03-15
- 환경: macOS, Docker Desktop 4.x
