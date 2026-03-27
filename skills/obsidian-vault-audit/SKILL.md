---
name: obsidian-vault-audit
description: Obsidian PARA Vault의 구조적 건강 상태를 진단하고 개선 포인트를 리포트합니다. 주기적 점검이나 Inbox 오버플로 시 사용.
metadata:
  author: workbench
  version: "1.5.0"
---

# obsidian-vault-audit: Obsidian PARA Vault 건강 진단

Obsidian PARA Vault의 구조적 건강 상태를 점검하고 개선 포인트를 리포트합니다.

## 전제조건

- `config.json`에 `vault` 경로가 설정되어 있어야 합니다
- Vault가 PARA 구조 (`0-Inbox/`, `1-Projects/`, `2-Areas/`, `3-Resources/`, `4-Archives/`)를 따라야 합니다

## 사용 상황

- 주기적 vault 점검 (월 1회 권장)
- 새 프로젝트/Area 추가 후 정합성 확인
- Inbox가 10개 이상 쌓였을 때

---

## 진단 절차

### 1. Vault 경로 확인

`config.json`에서 vault 경로를 읽습니다:
```json
{ "vault": "obsidian" }
```
→ workspace 루트 기준 상대경로. `${WORKSPACE}/${vault}/` 가 Vault 루트.

### 2. PARA 구조 총괄

각 PARA 폴더의 파일 수와 하위 폴더를 집계합니다.

```
| 카테고리 | 파일 수 | 상태 |
|----------|:-------:|------|
| 0-Inbox | N | ✅/⚠️ |
| 1-Projects | N | ✅ |
| 2-Areas | N | ✅/⚠️ |
| 3-Resources | N | ✅ |
| 4-Archives | N | ✅ |
```

### 3. 깨진 wikilink 탐지

Dashboard.md 및 Area 허브 문서의 `[[wikilink]]`가 실제 파일과 일치하는지 확인.

- `[[파일명]]` → vault 내에 `파일명.md` 존재 여부
- `[[파일명|표시명]]` → 파이프 앞부분(`파일명`)만 검증
- `[[폴더/파일명]]` → 상대경로 포함 링크

### 4. Area 허브 품질 비교

각 Area 폴더(`2-Areas/*/`)에 허브 파일이 있는지, 품질은 어떤지 평가합니다.

**허브 파일 탐지**: Area 폴더 내 폴더명과 동일한 .md 파일 (예: `2-Areas/건강/건강.md`)

**품질 등급:**

| 등급 | 기준 |
|------|------|
| ⭐⭐⭐ | 개요 + 하위 문서 테이블/목록 + 관련 프로젝트/리소스 링크 |
| ⭐⭐ | 허브 있으나 링크 불완전 또는 개요 없음 |
| ⭐ | 허브 있으나 내용 거의 없음 (< 200B) |
| ❌ | 허브 파일 자체가 없음 |

**체크 항목:**
- 폴더 내 모든 .md 파일이 허브에서 링크되는지
- 관련 1-Projects 프로젝트와 양방향 링크 존재하는지

### 5. Inbox 상태

| 점검 | 기준 |
|------|------|
| 오버플로 | 10개 이상이면 ⚠️ 경고 |
| Notion 잔여물 | `child_database` 주석만 있는 빈 파일 |
| 분류 가능 | 내용 기반 PARA 분류 대상 제안 |

Dashboard.md는 카운트에서 제외합니다.

### 6. 프로젝트-Area 크로스링크

활성 프로젝트(`1-Projects/*/TASK.md`에서 `status != done`)가 관련 Area 허브에서 링크되고 있는지 양방향 확인.

### 7. 빈 디렉토리 / 미사용 템플릿

- 비어있는 폴더 탐지 (`daily/`, `weekly/`, `guides/` 등)
- `_templates/`의 각 템플릿이 실제 사용되고 있는지

### 8. Dataview 쿼리 검증 (선택)

Dashboard.md에 Dataview 쿼리가 있으면 의도대로 동작하는지 논리 검증:
- FROM/WHERE 조건이 올바른 폴더/필드를 참조하는지
- frontmatter 필드(status, priority 등)가 실제 파일에 존재하는지

---

## 리포트 출력 형식

```markdown
# Vault 진단 리포트 (YYYY-MM-DD)

## 요약
| 항목 | 상태 |
|------|------|
| PARA 구조 | ✅/⚠️/❌ |
| 깨진 링크 | N건 |
| Area 허브 | N/M 양호 |
| Inbox | N건 |
| 크로스링크 | ✅/⚠️ |

## 상세
(항목별 진단 결과)

## 권장 조치
1. (우선순위순 개선 항목)
```

리포트는 `data/tasks/{현재task}/artifacts/` 또는 대화 내 직접 출력합니다.

---

## Dataview 쿼리 패턴 레퍼런스

### 프로젝트 목록 (폴더명으로 표시)
```
link(file.path, replace(file.folder, "1-Projects/", "")) AS "프로젝트"
```
→ `file.name = "TASK"` 필터 필수 (서브태스크 제외)

### 최근 수정 파일
```
dateformat(file.mtime, "MM-dd HH:mm") AS "수정일"
```

### wikilink 별칭
파일명과 표시명이 다를 때: `[[실제파일명|표시명]]`
