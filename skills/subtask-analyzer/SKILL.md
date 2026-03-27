---
name: subtask-analyzer
description: Analyzes codebase and environment before starting a subtask to generate detailed work instructions. Use when preparing SUBTASK.md with implementation plans and dependency analysis.
metadata:
  author: workbench
  version: "1.5.0"
---

# subtask-analyzer: 서브태스크 사전 분석

서브태스크를 시작하기 전에 코드베이스/환경을 분석하여 작업지시서(SUBTASK.md)를 생성합니다.

---

## 호출 시점

| 커맨드 | 동작 |
|--------|------|
| `wb-start` | 모든 서브태스크의 기본 SUBTASK.md 생성 (frontmatter + 목표만) |
| `wb-next` | **현재 서브태스크를 심층 분석**하여 SUBTASK.md 업데이트 |
| 수동 호출 | 특정 서브태스크 재분석 |

---

## wb-next 분석 프로세스

### 입력

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| task_path | O | vault 내 태스크 경로 |
| subtask_number | O | 서브태스크 번호 (예: 01) |

### 실행

```
1. SUBTASK.md 읽기 (vault/{task}/subtasks/{번호}-{이름}.md)
2. frontmatter에서 type 확인
3. type별 분석 수행:

[code 타입]
  a. 레포 worktree 경로 확인
  b. 분석 범위 제한 (아래 "분석 범위 제한" 섹션 참조)
  c. analyzer 에이전트 실행:
     - git diff {defaultBase}...HEAD 우선 분석
     - 관련 파일 탐색 (Glob + Grep, 범위 내)
     - 영향 범위 파악
     - 기존 패턴 확인
     - 테스트 전략 도출
  d. vault 검색 → SUBTASK.md `## 관련 지식`에 임베딩

[ops 타입]
  a. 사용 도구 확인 (MCP 도구, 외부 API)
  b. 필요 설정/인증 확인
  c. vault 검색 → SUBTASK.md `## 관련 지식`에 임베딩

[research 타입]
  a. 조사 범위 정의
  b. 관련 기존 지식 검색

[doc 타입]
  a. 문서화 대상 파악
  b. 기존 문서 확인

4. SUBTASK.md 업데이트:
   - ## 분석 섹션 채우기
   - ## 작업 체크리스트 생성
   - frontmatter: started 날짜 추가
```

### 분석 결과 포맷

```markdown
## 분석

### 영향 범위
- `src/payment/` — 신규 모듈 생성
- `src/order/service.ts:45-60` — 결제 호출 추가 필요
- `src/config/payment.config.ts` — 환경변수 추가

### 관련 지식
- [[nestjs-module-pattern]] — 모듈 생성 패턴
- [[pg-integration-guide]] — PG 연동 가이드 (3-Resources)

### 의존성
- #02 결제 UI → 이 서브태스크의 API 스펙에 의존
- 외부: PG사 sandbox 키 필요

### 리스크
- PG sandbox 응답 지연 가능 → 타임아웃 설정 필요
- 기존 결제 로직 없음 → 신규 설계 필요

## 작업 체크리스트
- [ ] PG 모듈 scaffolding
- [ ] 환경변수 설정
- [ ] API 엔드포인트 구현
- [ ] 에러 핸들링
- [ ] 단위 테스트
- [ ] 통합 테스트
```

---

## wb-start 초기 생성

`wb-start` 시에는 심층 분석 없이 기본 구조만 생성합니다.
**vault-conventions의 "SUBTASK.md 최소 템플릿"을 사용합니다.**

- 모든 서브태스크 폴더에 최소 SUBTASK.md를 생성 (첫 서브태스크만이 아님)
- subtask_type, depends, repo 등은 TASK.md의 서브태스크 정보에서 추출
- wb-next 실행 시 subtask-analyzer가 `## 분석`과 `## 작업 체크리스트`를 채움

---

## 분석 범위 제한

컨텍스트 소비를 줄이기 위해 분석 범위를 제한합니다:

### 파일 탐색 제한

```
1. git diff 우선: git diff {defaultBase}...HEAD로 변경 파일 먼저 분석
2. 디렉토리 필터링: 서브태스크 목표에서 관련 디렉토리 추론
3. 최대 파일 수: 탐색 대상 50개 파일 이내
4. 제외 경로:
   - node_modules/, dist/, build/, .next/
   - *.min.js, *.map, *.lock
   - vendor/, third_party/
```

### Vault 검색 제한

```
config.json `beta.fts-indexer` 확인:

FTS5 모드 (true):
  python3 tools/vault-search.py search "{query}" --vault {vault} --limit 10
  → JSON 결과에서 path, title, tldr 추출
  (Stage 3 전체 검색 불필요 — FTS5가 이미 전체 인덱스 검색)

grep 모드 (false/미설정):
  - Stage 1: frontmatter tags grep (경로 힌트 적용)
  - Stage 2: TL;DR 섹션 grep
  - Stage 3 (전체 vault grep): 사용하지 않음 (wb-recall 전용)

결과를 SUBTASK.md `## 관련 지식`에 임베딩
```

### 분석 결과 크기 제한

```
- 영향 범위: 파일 경로 + 라인 범위만 (코드 본문 X)
- 관련 지식: 제목 + TL;DR 한 줄만
- 작업 체크리스트: 10개 항목 이내
```

---

## 에이전트 사용

code 타입 분석 시 `analyzer` 에이전트를 사용합니다:

```
에이전트: analyzer (opus)
입력:
  - worktree 경로
  - 서브태스크 목표
  - 관련 vault 지식 (있으면)

출력:
  - 영향 범위 (파일 목록 + 라인)
  - 관련 패턴
  - 리스크
  - 작업 체크리스트 초안
```

---

## 활용 내역 표시

```
📊 subtask-analyzer 완료
├─ 🤖 Agents: analyzer (opus) - 코드 분석
├─ 💾 Vault: 검색 + SUBTASK.md 임베딩 (관련 지식 2건)
├─ 📝 SUBTASK.md 업데이트:
│   ├─ 영향 범위: 3개 파일
│   ├─ 작업 체크리스트: 6개 항목
│   └─ 리스크: 2건
└─ ⏱️ 소요: 15초
```
