---
name: vault-conventions
description: Obsidian vault PARA structure conventions and formats. Reference for all vault operations.
metadata:
  author: workbench
  version: "2.1.0"
---

# vault-conventions: Obsidian Vault 규칙

config.json의 `vault` 필드가 workspace 루트 기준 상대경로입니다.

## PARA 경로 매핑

| 경로 | 용도 |
|------|------|
| `{vault}/1-Projects/{task}/` | 활성 태스크 |
| `{vault}/1-Projects/{task}/subtasks/` | 서브태스크 |
| `{vault}/1-Projects/{task}/decisions.md` | 의사결정 기록 |
| `{vault}/3-Resources/` | 지식 저장 (패턴, 트러블슈팅, 가이드) |
| `{vault}/4-Archives/{task}/` | 완료 태스크 |
| `{vault}/0-Inbox/` | 미분류 캡처 |

## TASK.md 스키마

```yaml
---
type: code | ops          # 작업 유형
created: YYYY-MM-DD
tags: []                  # Obsidian 검색 + FTS5 인덱싱용 (optional)
lastScanned: ISO-8601     # 프론트로딩 staleness 감지 (optional)
---
```

서브태스크 체크리스트:
```
- [ ] 01. name → [[subtasks/01-name]]          # pending
- [ ] 01. name ⏳                               # in_progress
- [x] 01. name ✅ YYYY-MM-DD                    # done
- [ ] 01. name 🚫                               # blocked
- [~] 01. name (건너뜀: 사유)                    # skipped
- [-] 01. name (취소: 사유)                      # cancelled
```

## SUBTASK.md 스키마

```yaml
---
type: subtask
status: pending | in_progress | done | blocked | skipped | cancelled
subtask_type: code | ops | wait | doc | research
depends: []
repo: ""           # code 타입 전용
branch: ""         # code 타입 전용
created: YYYY-MM-DD
started: YYYY-MM-DD
---
```

## SUBTASK.md 최소 템플릿

서브태스크 디렉토리 생성 시 반드시 함께 생성해야 하는 최소 구조입니다.
wb-start, wb-add-subtask, wb-done(사후 보정) 등 모든 생성 경로에서 이 템플릿을 사용합니다.

```yaml
---
type: subtask
status: pending
subtask_type: {code|ops|wait|doc|research}
depends: []
repo: ""           # code 타입: 필수, 그 외: 빈 문자열
branch: ""         # code 타입: 필수, 그 외: 빈 문자열
created: YYYY-MM-DD
# started: YYYY-MM-DD  ← wb-next(subtask-analyzer)가 in_progress 전환 시 추가
---

# {번호}. {서브태스크 이름}

## 목표
{서브태스크 설명 또는 placeholder}

## 분석
> wb-next 시 subtask-analyzer가 채웁니다.

## 작업 체크리스트
> wb-next 시 자동으로 생성됩니다.

## 의사결정

## 히스토리
- [{created}] 생성
```

**생성 규칙:**
- 디렉토리 생성과 SUBTASK.md 생성은 항상 원자적으로 수행 (디렉토리만 있고 파일이 없는 상태 불허)
- subtask_type별 frontmatter: code는 repo/branch 필수, 나머지는 빈 문자열
- wb-next(subtask-analyzer)가 이미 존재하는 최소 템플릿을 발견하면, `## 분석`과 `## 작업 체크리스트` 섹션을 채우고 status를 in_progress로 변경
- wb-done이 SUBTASK.md 미존재를 발견하면, 이 최소 템플릿으로 생성 후 status: done으로 바로 설정

## decisions.md 포맷

```markdown
### YYYY-MM-DD: {title} {#anchor-id}
**서브태스크**: [[subtasks/01-xxx|서브태스크명]]
**컨텍스트**: {왜 필요했는지}
**결정**: {내용}
**대안**: {고려한 옵션}
**근거**: {선택 이유}
```

읽기 범위: wb-resume은 최근 5건, wb-done은 현재 서브태스크만, wb-end는 전체.

## Vault 저장 경로 (wb-memo용)

| 카테고리 | 접두어 | 저장 위치 |
|----------|--------|----------|
| 의사결정 | `[Decision]` | `1-Projects/{task}/decisions.md` |
| 트러블슈팅 | `[Troubleshoot]` | `3-Resources/troubleshooting/{title}.md` |
| 패턴 | `[Pattern]` | `3-Resources/patterns/{title}.md` |
| 가이드 | `[Guide]` | `3-Resources/guides/{title}.md` |
| Task 요약 | `[Task]` | `4-Archives/{task}/summary.md` |
| 메모 | `[Note]` | `3-Resources/{topic}/` 또는 `0-Inbox/` |

파일명: kebab-case. 모든 resource에 `## TL;DR` 섹션 필수.

## Tags 규칙

- 형식: YAML inline list `[tag1, tag2, tag3]`
- FTS5 인덱서가 자동 추출하여 검색 인덱싱
- 한국어 태그 가능 (kiwipiepy 토크나이저 적용)
- TASK.md, Resource 문서에 적용 (SUBTASK.md는 선택)

## Vault 검색

config.json의 `beta.fts-indexer` 설정에 따라 검색 방식이 결정됩니다.

### FTS5 모드 (beta.fts-indexer: true)

```bash
# 검색 (자동 싱크 포함)
python3 tools/vault-search.py search "{query}" --vault {vault} --limit 10

# 카테고리 필터
python3 tools/vault-search.py search "{query}" --vault {vault} --category Resources
```

결과: JSON 배열 (path, title, tags, tldr, category, rank)
→ grep/Read 없이 Bash 1회로 완료. 토큰 소모 최소.

**한국어 토크나이저 (v1.8.0+):**
kiwipiepy 설치 시 한국어 복합어를 형태소 단위로 분리하여 인덱싱합니다.
- "자산관리" → "자산 관리"로 검색 가능
- "피부관리", "운동루틴" 등 공백 없는 복합어도 매칭
- 미설치 시 기존 unicode61 기본 토크나이저로 fallback
- 설치: `pip install kiwipiepy`

### grep 모드 (beta.fts-indexer: false 또는 미설정, 기본값)

```
Stage 1: frontmatter tags grep (경로 힌트 적용)
  Grep: "tags:.*{query}" in {vault}/{hint-path}/**/*.md

Stage 2: TL;DR 섹션 grep
  Grep: query in ## TL;DR ~ 다음 ## 사이

(Stage 3 전체 vault grep은 /wb-recall에서만 허용)
```

경로 힌트:
| 쿼리 힌트 | 우선 검색 경로 |
|-----------|--------------|
| 트러블슈팅, 에러 | `3-Resources/troubleshooting/` |
| 패턴, 방법 | `3-Resources/patterns/`, `3-Resources/guides/` |
| 결정, 선택 | `1-Projects/*/decisions.md` |
| Task, 작업 | `4-Archives/*/summary.md` |

## data/tasks/ 역할

`data/tasks/{task}/`는 **작업 공간**입니다. Task 상태는 vault가 SSoT입니다.

| 위치 | 내용 | 예시 |
|------|------|------|
| **vault** (SSoT) | Task 상태, 서브태스크, 의사결정 | TASK.md, SUBTASK.md, decisions.md |
| **data/tasks/** | worktree, 히스토리, 임시 파일 | worktree/, history/, .claude 심링크 |

data/tasks/에 TASK.md 포인터를 생성할 수 있지만, 모든 상태 변경은 vault에서 수행합니다.
