---
name: skill-authoring-guide
description: Guides the creation of new skills following the agentskills.io standard and Workbench conventions, providing structure templates, naming rules, and validation checklists.
metadata:
  author: workbench
  version: "1.5.0"
---

# skill-authoring-guide: 스킬 작성 가이드

agentskills.io 국제표준에 따라 새 스킬을 작성하는 절차와 규칙을 안내합니다.

---

## 스킬 디렉토리 구조

```
skill-name/
├── SKILL.md              # 필수, <500줄
├── scripts/              # 선택: 실행 코드
├── references/           # 선택: 상세 문서
└── assets/               # 선택: 템플릿, 리소스
```

---

## 작성 절차

### 1. 이름 결정

- lowercase, hyphens only, 64자 이하
- 연속 하이픈 금지 (`my--skill` 불가)
- 디렉토리명과 `name` 필드 일치 필수

### 2. SKILL.md 생성

#### 필수 frontmatter

```yaml
---
name: my-skill
description: Processes payment webhooks and validates signatures when a new transaction event is received.
---
```

- `name`: kebab-case, 64자 이하, 디렉토리명과 동일
- `description`: 1024자 이하, 3인칭, what + when 포함

#### 선택 frontmatter

| 필드 | 설명 |
|------|------|
| `license` | 라이선스 식별자 (SPDX) |
| `compatibility` | 호환 플랫폼 목록 |
| `metadata` | key-value 쌍 (author, version 등) |
| `allowed-tools` | 허용 도구 목록 |

> 상세 스펙: [references/specification.md](references/specification.md)

#### Workbench 전용 확장

Workbench에서는 `metadata` 하위에 커스텀 필드를 배치합니다.

```yaml
metadata:
  author: workbench
  version: "1.4.0"
  skills: [vault-conventions]   # 의존 스킬
  agents: [analyzer]                        # 사용 에이전트
```

기존 Workbench 스킬의 최상위 `skills:`, `agents:` 필드도 계속 동작하지만, 표준 호환을 위해 `metadata` 하위를 권장합니다.

#### 본문 작성 규칙

- 500줄 이하 유지
- Claude가 이미 아는 것은 설명하지 않음
- 용어를 일관되게 사용
- 시간에 의존하는 정보 금지 ("최신 버전은 X" 등)
- 상세 내용은 `references/`로 분리

### 3. references/ 작성 (선택)

- SKILL.md에서 1단계 깊이로만 참조 (SKILL.md -> references/xxx.md)
- references 내부에서 다른 references를 참조하지 않음
- 필요시만 로드되는 상세 문서

### 4. 검증

최종 검증 체크리스트를 따라 확인합니다.

> 체크리스트: [references/checklist.md](references/checklist.md)

---

## Progressive Disclosure

스킬은 3단계로 점진 노출됩니다.

| 단계 | 내용 | 토큰 예산 |
|------|------|-----------|
| 1. Metadata | name + description | ~100 tokens |
| 2. Instructions | SKILL.md 본문 | <5000 tokens |
| 3. Resources | references/, scripts/ | 필요시만 |

이 단계를 염두에 두고 description을 충분히 설명적으로, 본문을 간결하게 작성합니다.

---

## 워크플로우 패턴

### 체크리스트 패턴

복잡한 프로세스는 체크리스트 형태로 작성합니다.

```markdown
### 프로세스
- [ ] 1단계: 입력 확인
- [ ] 2단계: 처리
- [ ] 3단계: 검증
```

### 피드백 루프

검증이 필요한 작업에는 validate -> fix -> repeat 패턴을 사용합니다.

```
1. 작성
2. 검증 (체크리스트 대조)
3. 오류 발견 시 수정 후 2번으로
4. 통과 시 완료
```

---

## 참조 문서

- [전체 스펙](references/specification.md) - frontmatter 필드별 상세 제약조건
- [예시 모음](references/examples.md) - 좋은/나쁜 예시, Workbench 스킬 예시
- [검증 체크리스트](references/checklist.md) - 최종 확인 항목
