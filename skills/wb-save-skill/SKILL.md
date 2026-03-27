---
name: wb-save-skill
description: Saves reusable knowledge as a workspace skill in SKILL.md format. Use when capturing recurring patterns or procedures for future reuse.
metadata:
  author: workbench
  version: "1.5.0"
---

# wb-save-skill: 지식을 Skill로 저장

반복될 지식을 Workspace Skill로 저장합니다.

## 입력
- `$ARGUMENTS`: Skill 이름 (선택)

## 프로세스

### 1. Skill 이름 결정

```
📝 Skill 이름 (예: pg-integration):
> pg-webhook
```

### 2. Skill 내용 수집

```
📝 어떤 상황에서 사용?
> PG webhook 설정할 때

핵심 내용?
> 타임아웃 30초, 재시도 3회

주의사항?
> 테스트/운영 URL 다름
```

### 3. Skill 파일 생성

`.claude/skills/pg-webhook/SKILL.md`:
```markdown
# pg-webhook: PG Webhook 설정

## 사용 상황
- PG webhook 설정 시

## 핵심 내용
- 타임아웃: 30초
- 재시도: 3회

## 주의사항
- 테스트/운영 URL 다름

## 출처
- Task: 결제 기능 (2024-02-06)
```

### 4. 저장 위치

```
Workspace .claude/skills/에 저장:
~/Workspaces/work/.claude/skills/pg-webhook/SKILL.md

(Core가 아닌 Workspace → 모든 Task가 공유)
```

### 5. 완료 메시지

```
✅ Skill 저장: pg-webhook

📁 위치: .claude/skills/pg-webhook/SKILL.md
📋 사용: /pg-webhook
```

## Skill vs Vault 메모

| | Vault | Skill |
|---|---|---|
| 저장 | 자동 | 명시적 |
| 형태 | 비구조화 | 구조화 마크다운 |
| 검색 | 자연어 | 명령어 (/name) |
| 용도 | 일회성 | 반복 패턴 |
