# Validation Checklist

새 스킬 작성 후 최종 검증 체크리스트입니다. 모든 항목을 통과해야 합니다.

---

## 필수 항목

### Frontmatter

- [ ] `name` 필드가 존재한다
- [ ] `name`이 kebab-case이다 (lowercase + hyphens only)
- [ ] `name`이 64자 이하이다
- [ ] `name`에 연속 하이픈(`--`)이 없다
- [ ] `name`이 하이픈으로 시작/끝나지 않는다
- [ ] `name`이 디렉토리명과 일치한다
- [ ] `description` 필드가 존재한다
- [ ] `description`이 1024자 이하이다
- [ ] `description`이 3인칭이다 (1인칭 "I"로 시작하지 않음)
- [ ] `description`에 what (무엇을 하는지)이 포함되어 있다
- [ ] `description`에 when (언제 사용하는지)이 포함되어 있다
- [ ] `description`에 시간 의존 표현이 없다

### SKILL.md 본문

- [ ] SKILL.md 파일이 디렉토리 루트에 위치한다
- [ ] 500줄 이하이다
- [ ] Claude가 이미 아는 일반 지식을 반복하지 않는다
- [ ] 용어가 일관적이다 (같은 개념에 다른 단어 사용 안 함)
- [ ] 시간에 의존하는 정보가 없다

### 구조

- [ ] 디렉토리명이 `name` 필드와 일치한다
- [ ] references/ 참조가 1단계 깊이만 사용한다
- [ ] references/ 파일 간 상호 참조가 없다

---

## Workbench 전용 항목

### metadata 확장

- [ ] `skills`, `agents` 필드가 metadata 하위에 위치한다 (최상위 아님)
- [ ] `version`이 현재 플러그인 버전과 일치한다
- [ ] `author`가 `workbench`로 설정되어 있다

### 내용

- [ ] 한국어로 작성되어 있다 (코드/예시 제외)
- [ ] 다른 스킬 참조 시 SKILL.md 경로를 사용한다

---

## Progressive Disclosure 확인

- [ ] description만으로 스킬의 용도를 판단할 수 있다
- [ ] SKILL.md 본문이 5000 tokens 이내이다 (대략 500줄 이하)
- [ ] 상세 내용은 references/로 분리되어 있다
- [ ] references/ 파일은 SKILL.md에서 명시적으로 링크되어 있다

---

## 검증 방법

1. 위 체크리스트를 순서대로 확인
2. 실패 항목 수정
3. 전체 통과할 때까지 반복
