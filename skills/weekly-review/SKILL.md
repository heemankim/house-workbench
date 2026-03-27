---
name: weekly-review
description: Generates weekly review summaries from vault data including completed tasks, decisions, and knowledge. Use when creating periodic review notes.
metadata:
  author: workbench
  version: "1.5.0"
---

# weekly-review: 주간 리뷰 자동 생성

vault 데이터를 기반으로 주간 리뷰를 자동 생성합니다.

---

## 호출

```
/wb-weekly-review
```

또는 Periodic Notes 플러그인의 주간 노트 생성 시 수동으로 참조.

---

## 프로세스

### 입력

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| week | - | 대상 주 (기본: 이번 주, 예: "2026-W08") |

### 실행

```
1. 대상 주의 날짜 범위 계산 (월~일)
2. vault 전체 스캔:

[1-Projects/ 스캔]
  a. 모든 TASK.md의 frontmatter + 체크리스트 파싱
  b. subtasks/*.md에서 started/completed 날짜가 대상 주에 해당하는 항목 수집
  c. 진행중 / 완료 / 블록된 서브태스크 분류

[4-Archives/ 스캔]
  d. 대상 주에 completed된 태스크 수집

[decisions.md 스캔]
  e. 대상 주에 기록된 의사결정 수집

[3-Resources/ 스캔]
  f. 대상 주에 생성/수정된 지식 노트 수집

3. 주간 리뷰 마크다운 생성
4. vault/weekly/{year}-W{week}.md에 저장
```

### 결과 포맷

```markdown
---
type: weekly-review
week: 2026-W08
period: 2026-02-16 ~ 2026-02-22
created: 2026-02-22
---

# 주간 리뷰: 2026-W08

## 이번 주 요약

| 항목 | 수치 |
|------|------|
| 완료 서브태스크 | 5개 |
| 신규 서브태스크 | 2개 |
| 의사결정 | 3건 |
| 새 지식 노트 | 2건 |
| 완료 태스크 | 1개 |

## 프로젝트 현황

### [[1-Projects/결제-기능/TASK|결제 기능]] (진행중)
- [x] 01. PG 모듈 구현 (완료: 02-17)
- [x] 02. 결제 UI (완료: 02-19)
- [ ] 03. 통합 테스트 (진행중)

### [[1-Projects/로그인-버그/TASK|로그인 버그]] (진행중)
- [x] 01. 원인 분석 (완료: 02-18)
- [ ] 02. 수정 및 배포 (대기)

## 완료된 태스크
- [[4-Archives/API-리팩토링/TASK|API 리팩토링]] — 02-20 완료

## 주요 의사결정
1. [[결제-기능/decisions#JWT-vs-Session|JWT vs Session]] → JWT 채택
2. [[결제-기능/decisions#PG-선택|PG사 선택]] → Stripe
3. [[로그인-버그/decisions#세션-전략|세션 전략]] → Redis 클러스터

## 새로 추가된 지식
- [[3-Resources/patterns/pg-integration-pattern|PG 연동 패턴]]
- [[3-Resources/troubleshooting/redis-cluster-failover|Redis 클러스터 페일오버]]

## PARA 메인터넌스

> 주간 리뷰 시 점검 항목

- [ ] 0-Inbox에 미분류 노트 없는지 확인
- [ ] 완료된 프로젝트 → 4-Archives 이동 확인
- [ ] 3-Resources에 태그 정리
- [ ] 2-Areas 관련 업데이트 필요한지 확인

## 다음 주 계획
> 자동 생성: 현재 진행중인 서브태스크 기준

1. 통합 테스트 완료 (결제 기능 #03)
2. 로그인 버그 수정 및 배포 (#02)
```

---

## 생성 위치

```
{vault}/weekly/{year}-W{week}.md
예: obsidian/weekly/2026-W08.md
```

---

## 활용 내역 표시

```
📊 /wb-weekly-review 완료
├─ 📋 스캔: 1-Projects (3개), 4-Archives (1개)
├─ 📝 서브태스크: 완료 5개, 진행 2개, 블록 0개
├─ 💡 의사결정: 3건
├─ 📚 새 지식: 2건
├─ 📁 저장: weekly/2026-W08.md
└─ ⏱️ 소요: 8초
```

---

## Periodic Notes 연동

Obsidian Periodic Notes 플러그인 설정:
- Weekly note folder: `weekly`
- Weekly note format: `YYYY-[W]ww`
- Weekly note template: `_templates/tpl-weekly.md`

> tpl-weekly.md에 Dataview 쿼리를 포함하면 Obsidian에서도 동적 집계가 가능합니다.
> `/wb-weekly-review`는 더 상세한 분석과 PARA 메인터넌스 체크리스트를 추가합니다.
