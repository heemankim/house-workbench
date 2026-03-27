---
name: wb-end
description: Completes an entire task, archives subtasks, extracts knowledge, and generates a final summary. Use when all subtasks are done and the task is ready to close.
metadata:
  author: workbench
  version: "2.1.0"
  skills:
    - vault-conventions
  agents:
    summarize: workbench:analyzer
    review: workbench:reviewer
---

# wb-end: Task 완료

Task 전체를 완료하고 정리합니다.

## 입력
- `$ARGUMENTS`: Task 이름 (선택)

## 프로세스

### 1. Task 유형 및 서브태스크 상태 확인

#### code 유형
```
📋 서브태스크 (code):
✅ 1. PG 연동 (PR #123 merged)
✅ 2. 결제 UI (PR #124 merged)
✅ 3. 통합 테스트 (PR #125 open)
```

#### ops 유형
```
📋 서브태스크 (ops):
✅ 1. API 키 설정
✅ 2. 워크플로우 생성 (n8n workflow #42)
✅ 3. 슬랙 연동
✅ 4. 테스트 완료
```

미완료 있으면 경고

---

## Code 유형 프로세스

### 2c. 전체 요약 작성

```
📝 Task 요약:

## 완료된 작업
- PG 연동 (Stripe)
- 결제 UI (모달 방식)

## 주요 의사결정
- Stripe 선택 (수수료, API 품질)
- webhook 타임아웃 30초

## PR 목록
- #123, #124, #125
```

### 3c. 워크트리 정리

```
🧹 워크트리 정리 중...
브랜치는 유지 (PR 열려있을 수 있음)
```

### 4c. 완료 메시지 (code)

```
┌─────────────────────────────────────────────────────────┐
│ ✅ Task 완료: 결제 기능                                   │
│ 📦 유형: code                                           │
├─────────────────────────────────────────────────────────┤
│ 📊 요약:                                                │
│  ├─ 서브태스크: 3개 완료                                 │
│  ├─ PR: 3개 (모두 merged)                               │
│  └─ 기간: 3일                                           │
│                                                         │
│ 💾 저장됨:                                              │
│  ├─ Vault: Task 요약, 의사결정 5건                  │
│  └─ 지식 승격 제안: 3건 (Skill 1, Command 1, 업데이트 1)  │
└─────────────────────────────────────────────────────────┘
```

---

## Ops 유형 프로세스

### 2o. 전체 요약 작성

```
📝 Task 요약:

## 완료된 작업
- OpenWeather API 연동
- n8n 워크플로우 생성 (매일 오전 7시 실행)
- 슬랙 알림 연동

## 주요 의사결정
- 무료 플랜 API 한도 (60회/분) → 캐싱 적용
- 알림 채널: #weather-alerts

## 생성된 결과물
- n8n workflow #42: "Daily Weather Alert"
- artifacts/workflow-config.json
- artifacts/slack-webhook-test.png
```

### 3o. 결과물 정리

```
📎 생성된 결과물:
  ├─ n8n workflow #42 (활성화됨)
  ├─ artifacts/workflow-config.json
  └─ artifacts/slack-webhook-test.png

결과물을 유지할까요? (Y/n)
```

### 4o. 완료 메시지 (ops)

```
┌─────────────────────────────────────────────────────────┐
│ ✅ Task 완료: 날씨 자동화                                 │
│ 🔧 유형: ops                                            │
├─────────────────────────────────────────────────────────┤
│ 📊 요약:                                                │
│  ├─ 서브태스크: 4개 완료                                 │
│  ├─ 생성 결과물: 3개                                    │
│  └─ 기간: 1일                                           │
│                                                         │
│ 🛠️ 활성화된 도구:                                       │
│  └─ n8n workflow #42 (매일 오전 7시)                    │
│                                                         │
│ 💾 저장됨:                                              │
│  ├─ Vault: Task 요약, 의사결정 3건                  │
│  └─ 지식 승격 제안: 2건 (Skill 1, 업데이트 1)            │
└─────────────────────────────────────────────────────────┘
```

---

## 공통 프로세스

### Vault 저장

```
💾 Vault 저장:
- Task 요약
- 주요 의사결정
- 트러블슈팅 기록
```

### 지식 승격 제안

Task 완료 시 컨텍스트를 분석하여 재사용 가능한 지식을 제안합니다.

#### 분석 대상

```
분석 소스:
├── TASK.md (의사결정, 범위, 서브태스크)
├── 커밋 히스토리 및 코드 변경
├── Vault에 저장된 이 Task의 기록
├── 작업 중 반복된 패턴
└── 기존 Workspace skills와의 관련성
```

#### 제안 유형

| 유형 | 조건 | 저장 위치 |
|------|------|-----------|
| **Skill 생성** | 재사용 가능한 패턴/가이드 발견 | `.claude/skills/{name}/SKILL.md` |
| **Command 생성** | 반복 가능한 워크플로우 발견 | `.claude/skills/{name}/SKILL.md` (frontmatter로 커맨드 등록) |
| **기존 Skill 업데이트** | 기존 스킬에 새 정보 추가 가능 | 기존 `SKILL.md`에 append |

#### 제안 프로세스

```
1. 컨텍스트 수집
   → TASK.md, 커밋 로그, 의사결정 로그 분석

2. 패턴 감지
   → 반복된 작업, 트러블슈팅 해결책, 설정 패턴

3. 기존 스킬 대조
   → .claude/skills/ 내 기존 스킬과 비교
   → 새로 만들지, 기존에 추가할지 판단

4. 제안 출력 + 사용자 선택
```

#### 출력 예시

```
💡 지식 승격 제안 (3건)

1. 📚 [Skill 생성] "Stripe 연동 가이드"
   → webhook 타임아웃, 재시도 로직, 테스트/운영 URL
   → 이유: 의사결정 3건 + 트러블슈팅 2건 감지

2. 🔧 [Command 생성] "/deploy-staging"
   → 스테이징 배포 → 스모크 테스트 → 슬랙 알림 워크플로우
   → 이유: 서브태스크 3개에서 동일 배포 패턴 반복

3. 📝 [Skill 업데이트] "api-patterns.md"에 추가
   → PG webhook 에러 핸들링 섹션
   → 이유: 기존 API 패턴 스킬에 관련 내용 없음

저장할 항목을 선택하세요 (번호, 쉼표 구분):
> 1, 3

건너뛰려면 Enter
```

#### 저장 처리

- **Skill 생성**: `/wb-save-skill` 프로시저에 따라 `.claude/skills/`에 저장
- **Command 생성**: 동일하게 `.claude/skills/`에 저장하되, frontmatter에 커맨드 메타데이터 포함
- **Skill 업데이트**: 기존 파일의 관련 섹션에 내용 추가

### Task 히스토리 저장 및 폴더 정리

Workspace의 `data/history/{task-name}.md`에 요약을 저장한 후 Task 폴더를 삭제합니다.

#### 히스토리 파일 템플릿

```markdown
# Task: {task-name}

**유형:** {type} | **레포:** {repo} | **기간:** {start} ~ {end}
**PR:** [#{number}]({url}) → {base}

## 완료된 작업
- {요약 항목들}

## 주요 의사결정
- {의사결정 항목들}

## 변경 파일
- {파일 (+추가 -삭제)}

## 커밋
- {hash}: {message}
```

#### 정리

```bash
# 1. 히스토리 저장
# data/history/{task-name}.md 생성 (위 템플릿)

# 2. 히스토리 저장 확인
# data/history/{task-name}.md가 정상 생성되었는지 확인

# 3. Task 폴더 삭제 (사용자 확인)
```

```
⚠️ Task 폴더를 삭제합니다: data/tasks/{task-name}/
   히스토리: data/history/{task-name}.md 저장 완료

계속할까요? (Y/n)
```

```bash
# 확인 후 삭제
rm -rf data/tasks/{task-name}/
```

> Worktree는 이 단계 전에 이미 정리됩니다 (3c 단계).
> 브랜치는 PR이 open이면 유지합니다.

---

## 지식 축적

```
Task 완료
├── data/history/{task-name}.md 저장 (자동)
│   └─ 요약, PR, 커밋, 의사결정
├── Vault 저장 (자동)
│   ├─ Task 요약
│   ├─ 의사결정
│   └─ 트러블슈팅
└── 지식 승격 제안 (선택)
    ├─ Skill 생성: 재사용 패턴/가이드
    ├─ Command 생성: 반복 워크플로우
    └─ 기존 Skill 업데이트: 새 정보 추가
```

### Task 매니저 동기화

> ⚠️ vault 아카이빙(1-Projects → 4-Archives)을 먼저 수행한 후, data/tasks/ 폴더를 정리합니다.

vault TASK.md를 완료 처리하고 4-Archives/로 이동합니다.

---

## 활용 내역 표시

커맨드 실행 후 사용된 리소스를 표시:

### code 유형
```
📊 /wb-end 실행 완료
├─ 📦 Type: code
├─ 🤖 Agents:
│   ├─ analyzer (opus) - Task 요약 생성
│   └─ reviewer (haiku) - 최종 검토
├─ 💾 Vault:
│   ├─ Vault 저장 (Task 요약, 의사결정 5건)
│   └─ 지식 승격 제안 {N}건
├─ 📚 Skills: vault-conventions
├─ 🔧 Actions:
│   ├─ 서브태스크 상태 확인
│   ├─ Worktree 정리
│   ├─ data/history/{task-name}.md 저장
│   ├─ Task 폴더 삭제
│   └─ Vault 저장
└─ ⏱️ 소요: 15초
```

### ops 유형
```
📊 /wb-end 실행 완료
├─ 🔧 Type: ops
├─ 🤖 Agents:
│   ├─ analyzer (opus) - Task 요약 생성
│   └─ reviewer (haiku) - 최종 검토
├─ 💾 Vault:
│   ├─ Vault 저장 (Task 요약, 의사결정 3건)
│   └─ 지식 승격 제안 {N}건
├─ 📚 Skills: vault-conventions
├─ 🛠️ Tools: n8n-mcp (워크플로우 활성화 확인)
├─ 🔧 Actions:
│   ├─ 서브태스크 상태 확인
│   ├─ 결과물 정리
│   ├─ data/history/{task-name}.md 저장
│   ├─ Task 폴더 삭제
│   └─ Vault 저장
└─ ⏱️ 소요: 12초
```
