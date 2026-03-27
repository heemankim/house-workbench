---
name: wb-update
description: Updates the Workbench plugin from source, syncs cache, and applies workspace migrations. One command for the full update flow.
metadata:
  author: workbench
  version: "1.7.0"
---

# wb-update: Workspace 업데이트

플러그인 소스 업데이트부터 캐시 동기화, 마이그레이션까지 한 번에 처리합니다.

## 입력
- `$ARGUMENTS`: 없음

## 프로세스

### 0. 플러그인 소스 업데이트 및 캐시 동기화

사용자가 수동으로 git pull이나 cp를 할 필요 없이, `/wb-update` 한 번으로 전부 처리합니다.

#### 0-1. 소스 경로 확인

```
소스 경로 탐색 순서:
1. config.json의 pluginSource (있으면)
2. ~/.workbench/core (기본 설치 경로)

없으면:
  "⚠️ 플러그인 소스를 찾을 수 없습니다."
  "~/.workbench/core에 클론하거나 config.json에 pluginSource를 설정하세요."
  → 소스 업데이트 건너뛰고 기존 캐시로 마이그레이션만 진행
```

#### 0-2. git pull (소스 최신화)

```bash
cd {소스 경로} && git pull origin main
```

```
📥 플러그인 소스 업데이트 중...
✅ 최신 버전 가져옴 (v1.7.0)
```

실패 시 (오프라인, 권한 문제 등):
```
⚠️ git pull 실패 (오프라인?). 기존 소스로 진행합니다.
```

#### 0-3. 캐시 동기화

소스에서 플러그인 캐시로 파일을 동기화합니다.

```
캐시 경로 탐색:
~/.claude/plugins/cache/workbench-local/workbench/ 하위에서
현재 활성 캐시 폴더 찾기 (가장 최신 수정 시간)
```

```bash
# .git, __pycache__ 제외하고 cp -R 동기화
# ⚠️ rsync는 Claude Code 샌드박스에서 동작하지 않음 — 반드시 cp 사용
find {소스} -path '*/.git' -prune -o -path '*/__pycache__' -prune -o -type f -print0 | while IFS= read -r -d '' f; do
  rel="${f#{소스}/}"
  dest="{캐시}/$rel"
  mkdir -p "$(dirname "$dest")"
  cp "$f" "$dest"
done
```

```
📦 캐시 동기화 중...
✅ 캐시 업데이트 완료 ({캐시 경로})
```

> **중요**: `.git` 폴더는 반드시 제외합니다. 캐시의 `.git/objects`에 쓰기 권한이 없어
> `cp -R`이 실패합니다. 위 `find + cp` 패턴으로 파일 단위 복사를 사용하세요.

#### 0-4. 소스/캐시 버전 일치 확인

```
소스 plugin.json version: 1.7.0
캐시 plugin.json version: 1.7.0  ← 동기화 후 일치해야 함
```

불일치 시 경고:
```
⚠️ 소스(1.7.0)와 캐시(1.6.0) 버전이 다릅니다.
캐시 동기화에 문제가 있을 수 있습니다.
수동으로 확인하세요: {캐시 경로}
```

### 1. 버전 확인

```
플러그인 버전: 캐시의 plugin.json version 읽기 (Step 0에서 동기화된 최신)
워크스페이스 버전: config.json의 pluginVersion 읽기 (없으면 "1.0.0")

비교:
  동일 → "이미 최신 버전입니다."
  다름 → 마이그레이션 필요
```

### 2. 마이그레이션 목록 조회

`migrations/` 폴더에서 워크스페이스 버전 초과 ~ 플러그인 버전 이하의 파일을 순서대로 조회:

```
예: 워크스페이스 1.5.0 → 플러그인 1.7.0
적용 대상: v1.6.0.md, v1.7.0.md (순서대로)
```

파일명 규칙: `v{major}.{minor}.{patch}.md`

### 3. 변경 사항 요약

```
🔄 Workbench 업데이트

현재: v1.5.0 → 최신: v1.7.0

📋 마이그레이션 목록:
1. [v1.6.0] FTS5 Vault 인덱서 (Beta)
2. [v1.7.0] wb-update 원스톱 업데이트

적용하시겠습니까? (Y/n)
```

### 4. 마이그레이션 실행

각 마이그레이션 파일을 순서대로 읽고 실행합니다.

마이그레이션 파일의 `## 자동 마이그레이션` 섹션의 지시를 따릅니다:

```
🔄 [v1.6.0] 실행 중...

✅ beta 블록 추가 완료
✅ tools/vault-search.py 배치 완료

🔄 [v1.6.0] 완료
```

각 마이그레이션의 `## 수동 확인` 섹션이 있으면 사용자에게 안내:

```
⚠️ 수동 확인 필요:
- config.json에서 beta.fts-indexer: true 설정 시 FTS5 활성화
```

### 5. Beta 기능 마이그레이션

config.json에 `beta` 블록이 없으면 추가합니다:

```json
{
  "beta": {}
}
```

`beta.fts-indexer` 활성화 안내:
```
🧪 Beta 기능: FTS5 Vault 인덱서

Vault 검색을 SQLite FTS5로 전환하면 토큰 소모를 크게 줄일 수 있습니다.
활성화하시겠습니까? (y/N)

→ y 선택 시:
  1. config.json에 "beta": { "fts-indexer": true } 추가
  2. tools/vault-search.py 존재 확인 (없으면 플러그인에서 복사)
  3. 초기 인덱싱 실행: python3 tools/vault-search.py index --vault {vault}
  4. "인덱싱 완료 (N파일, DB크기)" 표시

→ n 선택 시:
  config.json에 "beta": {} 추가 (빈 블록)
  기존 2-stage grep 유지
```

### 6. config.json 업데이트

```json
{
  "pluginVersion": "{플러그인 버전}"
}
```

config.json에 `pluginVersion` 필드를 추가하거나 업데이트합니다.

### 7. 변경점 안내 (What's New)

마이그레이션 완료 후, 각 마이그레이션 파일의 `## What's New` 섹션을 모아서 사용자에게 표시합니다.

```
📢 What's New in v1.7.0

  원스톱 업데이트
  ├─ /wb-update 한 번으로 소스 pull + 캐시 동기화 + 마이그레이션
  ├─ 수동 git pull, cp 불필요
  └─ 오프라인 시 기존 캐시로 자동 fallback
```

### 8. 완료 메시지

```
┌─────────────────────────────────────────────────────────┐
│ ✅ Workspace 업데이트 완료                                │
├─────────────────────────────────────────────────────────┤
│ 📦 버전: v1.5.0 → v1.7.0                                │
│ 📋 적용된 마이그레이션: 2건                               │
│                                                         │
│ 변경 내역:                                               │
│  ├─ [v1.6.0] FTS5 Vault 인덱서 (Beta)                   │
│  └─ [v1.7.0] wb-update 원스톱 업데이트                   │
│                                                         │
│ 💡 /wb-status로 현재 상태를 확인하세요                    │
└─────────────────────────────────────────────────────────┘
```

## 이미 최신인 경우

```
✅ 이미 최신 버전입니다. (v1.7.0)
업데이트할 내용이 없습니다.
```

## 소스는 최신이지만 캐시만 다른 경우

Step 0에서 캐시 동기화 후 버전이 같아지면:
```
📦 캐시 동기화 완료 (v1.7.0)
✅ 이미 최신 버전입니다. 마이그레이션 불필요.
```

## 마이그레이션 없이 버전만 다른 경우

```
🔄 Workbench 업데이트

현재: v1.7.0 → 최신: v1.7.1

이 버전에는 마이그레이션이 필요하지 않습니다.
pluginVersion만 업데이트합니다.

✅ config.json pluginVersion → v1.7.1
```

## config.json pluginSource 설정

기본 소스 경로(`~/.workbench/core`)를 변경하려면:

```json
{
  "pluginSource": "/path/to/workbench/repo"
}
```

## 활용 내역

```
📊 /wb-update 실행 완료
├─ 📥 소스: git pull 완료 ({소스 경로})
├─ 📦 캐시: 동기화 완료 ({캐시 경로})
├─ 📦 버전: v{이전} → v{최신}
├─ 📋 Migrations: {적용 건수}건
├─ 🔧 Actions:
│   ├─ {마이그레이션별 작업 내역}
│   └─ config.json pluginVersion 업데이트
└─ ⏱️ 소요: {시간}
```
