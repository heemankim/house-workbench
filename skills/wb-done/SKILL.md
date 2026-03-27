---
name: wb-done
description: Completes the current subtask, syncs task manager, and extracts decisions and knowledge. Use when finishing a subtask to record progress and move forward.
metadata:
  author: workbench
  version: "2.1.0"
  skills:
    - vault-conventions
  agents:
    review: workbench:reviewer
    check: workbench:checker
    test: workbench:tester
---

# wb-done: 서브태스크 완료

현재 서브태스크를 완료 처리합니다.

## 입력
- `$ARGUMENTS`: 없음

## 프로세스

### 0. SUBTASK.md 존재 확인 (가드레일)

> vault SUBTASK.md를 먼저 확인/생성하고, data/tasks/에도 미러링합니다.

SUBTASK.md가 없는 경우 사후 보정합니다:

```
SUBTASK.md 미존재 감지:
→ "⚠️ SUBTASK.md가 없어서 자동 생성합니다"
→ vault-conventions 최소 템플릿으로 생성
→ TASK.md의 서브태스크 라인에서 이름, 유형 추출
→ 대화 컨텍스트에서 작업 요약 추출
→ status: done, completed: {오늘 날짜}로 설정
→ 정상 완료 프로세스 계속
```

이 가드레일은 wb-start/wb-add-subtask가 정상 동작했으면 실행되지 않는 마지막 안전망입니다.

### 1. 현재 서브태스크 및 유형 확인

```
📍 현재 서브태스크: PG 연동 (1/6)
📦 서브태스크 유형: code
```

**서브태스크 유형:**
| 유형 | 아이콘 | 설명 |
|------|--------|------|
| `code` | 📦 | 코드 작업 (PR 생성) |
| `ops` | 🔧 | 운영/설정 작업 |
| `wait` | ⏳ | 대기/협의 (외부 의존) |
| `doc` | 📝 | 문서 작업 |
| `research` | 🔍 | 조사/분석 |

---

## Code 유형 프로세스

### 1.5c. 자동 wb-check 게이트 (code 유형)

code 유형 서브태스크는 완료 전 자동으로 설계-구현 검증을 실행합니다:

```
📋 /wb-done 시작
↓
🤖 /wb-check 자동 호출
↓
Match Rate 판정:
├─ >= 90% ✅ → 계속 진행
├─ 70-89% ⚠️ → "Gap이 있습니다. 진행할까요?" 확인
└─ < 70% ❌ → 중단, 설계 재검토 필요
```

`/wb-done --skip-check`로 게이트를 건너뛸 수 있습니다 (비권장).

### 1.6c. Release 체크리스트 (code 유형)

wb-check 통과 후 다음 항목을 검증합니다:

```
📋 Release 체크리스트:
☐ README 갱신 필요 여부 확인
☐ 마이그레이션 파일 필요 여부 확인
☐ 버전 범프 필요 여부 확인
☐ 커밋 메시지 Conventional Commits 준수
☐ 민감 정보 미포함
```

각 항목 미충족 시 확인 후 진행 또는 중단을 선택합니다.

> 📊 상세 체크리스트: [Release Process](references/release-process.md) 참조

### 2c. 미커밋 변경사항 확인

```
⚠️ 미커밋 변경사항:
  - backend/src/pg.ts (modified)

커밋하시겠습니까? (Y/n)
```

### 3c. 서브태스크 요약

```
📝 이 서브태스크에서 완료한 작업:
> PG 연동 완료, webhook 설정, 결제 API 구현
```

### 4c. 히스토리 업데이트

```markdown
### 서브태스크 완료: PG 연동 - HH:MM

#### 요약
PG 연동 완료, webhook 설정, 결제 API 구현

#### 커밋
- abc1234: feat: PG 연동 구현
```

### 5c. 완료 메시지 (code)

```
┌─────────────────────────────────────────────────────────┐
│ ✅ 서브태스크 완료: PG 연동                               │
│ 📦 유형: code                                           │
├─────────────────────────────────────────────────────────┤
│ 📝 요약: PG 연동 완료, webhook 설정, 결제 API 구현       │
│ 📊 커밋: 3개                                            │
│ 📁 변경: 5개 파일 (+234, -12)                           │
│ ✅ wb-check: Match Rate 92%, Coverage 85%           │
│ ✅ Release 체크리스트: 통과                           │
└─────────────────────────────────────────────────────────┘

🔀 PR을 생성하시겠습니까?
- /wb-pr로 PR 생성
- /wb-next로 다음 서브태스크
```

---

## Ops 유형 프로세스

### 2o. 작업 결과 확인

```
🔍 작업 결과를 확인합니다:

✅ 완료된 작업:
  - OpenWeather API 키 환경변수 설정
  - API 연결 테스트 성공

📎 결과물:
  - artifacts/openweather-test.json (API 응답 샘플)
```

### 3o. 서브태스크 요약

```
📝 이 서브태스크에서 완료한 작업:
> OpenWeather API 키 설정 및 연결 테스트 완료
```

### 4o. 결과물 저장 (선택)

```
💾 결과물을 artifacts 폴더에 저장할까요?
- 설정 파일
- 스크린샷
- API 응답 샘플
- 기타

> (파일명 또는 건너뛰기)
```

### 5o. 히스토리 업데이트

```markdown
### 서브태스크 완료: API 키 설정 - HH:MM

#### 요약
OpenWeather API 키 설정 및 연결 테스트 완료

#### 사용된 도구
- n8n-mcp: HTTP Request 노드 테스트

#### 결과물
- artifacts/openweather-test.json
```

### 6o. 완료 메시지 (ops)

```
┌─────────────────────────────────────────────────────────┐
│ ✅ 서브태스크 완료: API 키 설정                          │
│ 🔧 유형: ops                                            │
├─────────────────────────────────────────────────────────┤
│ 📝 요약: OpenWeather API 키 설정 및 연결 테스트         │
│ 🛠️ 사용 도구: n8n-mcp                                   │
│ 📎 결과물: 1개 (artifacts/)                             │
└─────────────────────────────────────────────────────────┘

다음 단계:
- /wb-next로 다음 서브태스크
```

---

> 📎 wait, doc, research 유형의 상세 프로세스는 [추가 유형 프로세스](references/additional-types.md)를 참조하세요.

---

## 공통 프로세스

### 의사결정 저장 확인

```
💡 중요한 결정이 있었나요?
> Stripe 선택, webhook 타임아웃 30초
```

또는 (ops)

```
💡 중요한 결정이 있었나요?
> 무료 플랜 API 한도 60회/분, 캐싱 필요
```

### TASK.md 업데이트

```markdown
## 서브태스크
- [x] 01. PG 연동 ← 완료
- [ ] 02. 결제 UI
```

또는 (ops)

```markdown
## 서브태스크
- [x] 01. API 키 설정 ← 완료
- [ ] 02. 워크플로우 생성
```

### Vault 업데이트 (SSoT)

**vault가 SSoT입니다.** 모든 상태 변경은 vault를 먼저 업데이트합니다:

1. vault TASK.md 체크리스트: `- [x] ✅ {날짜}` 형식으로 업데이트
2. vault SUBTASK.md: status를 `done`, completed 날짜 기록
3. data/tasks/ SUBTASK.md: vault와 동일하게 미러링

---

## 활용 내역 표시

커맨드 실행 후 사용된 리소스를 유형별로 표시합니다.

> 📎 유형별 상세 표시 형식은 [활용 내역 표시](references/usage-display.md)를 참조하세요.
