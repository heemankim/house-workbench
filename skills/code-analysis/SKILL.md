---
name: code-analysis
description: Performs symbolic code analysis using Serena MCP. Use when exploring codebases, resolving symbols, or analyzing dependencies during task planning and implementation.
metadata:
  author: workbench
  version: "1.5.0"
---

# code-analysis: Serena 기반 코드 분석

Serena MCP를 활용한 심볼릭 코드 분석 스킬입니다.
코드 탐색이 필요한 커맨드(wb-plan, wb-start 등)에서 자동으로 사용됩니다.

## 설정 (config.json)

```json
{
  "adapters": {
    "codeAnalysis": {
      "type": "serena",
      "enabled": true
    }
  }
}
```

**비활성화 시:** Grep/Glob 기반 탐색으로 fallback

---

## 프로젝트 활성화

Serena의 심볼릭 도구를 사용하려면 먼저 프로젝트를 활성화해야 합니다.

### 활성화 프로세스

```
1. mcp__serena__activate_project({ project: "{repo_path}" })
2. mcp__serena__check_onboarding_performed()
   → 온보딩 안 됨 → mcp__serena__onboarding() 실행
   → 온보딩 완료 → 바로 사용 가능
```

### 자동 활성화 시점

| 커맨드 | 활성화 대상 | 시점 |
|--------|------------|------|
| `/wb-add-repo` | 추가된 레포 | 클론 완료 후 |
| `/wb-plan` | 분석 대상 레포 | 코드 탐색 전 |
| `/wb-start` | 선택된 레포 | worktree 생성 후 |
| `/wb-resume` | 현재 Task의 레포 | 컨텍스트 복원 시 |

---

## 도구 사용 가이드

### 심볼 탐색 (Serena 우선)

| 목적 | Serena 도구 | Fallback |
|------|------------|----------|
| 파일 내 심볼 목록 | `get_symbols_overview` | Grep |
| 심볼 정의 찾기 | `find_symbol` (include_body) | Grep |
| 참조/호출처 추적 | `find_referencing_symbols` | Grep |
| 심볼 이름 변경 | `rename_symbol` | 수동 Edit |
| 패턴 검색 | `search_for_pattern` | Grep |
| 파일 찾기 | `find_file` | Glob |

### 텍스트 검색 (Grep 우선)

다음은 Serena가 아닌 Grep이 더 적합합니다:
- 로그 메시지, 설정값 찾기
- 주석/문서 내 텍스트 검색
- 비코드 파일 (yaml, json, md) 검색

### 사용 전략

```
1. 심볼 이름을 알 때 → find_symbol (정확하고 빠름)
2. 구조 파악할 때 → get_symbols_overview (토큰 절약)
3. 영향도 분석 시 → find_referencing_symbols (호출 관계)
4. 이름 모를 때 → search_for_pattern → find_symbol
5. 비코드 검색 → Grep (Serena 대상 아님)
```

---

## wb-plan 연동

코드 탐색 단계에서 Serena를 활용하는 패턴:

```
1. 엔티티/모델 파악
   → get_symbols_overview("src/entities/") 또는 find_symbol("*Entity")
   → 상태값, 관계 구조 확인

2. 서비스 로직 파악
   → find_symbol("{ServiceName}") → depth=1로 메서드 목록
   → 필요한 메서드만 include_body=True로 읽기

3. 이벤트/핸들러 추적
   → find_referencing_symbols("{EventName}")
   → 기존 이벤트 구조 파악

4. API 엔드포인트 파악
   → search_for_pattern("@(Get|Post|Put|Delete)")
   → 외부 인터페이스 목록
```

---

## 온보딩 정보 활용

온보딩 시 Serena가 생성하는 프로젝트 메모리:
- 프로젝트 구조 개요
- 주요 심볼 및 패턴
- 빌드/테스트 방법

이 정보는 이후 대화에서 `mcp__serena__read_memory`로 재활용됩니다.
