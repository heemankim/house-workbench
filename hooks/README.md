# Workbench Hooks

Claude Code hooks를 사용한 자동화입니다.

## 지원 이벤트

| 이벤트 | 시점 | 용도 |
|--------|------|------|
| `SessionStart` | 세션 시작 시 | 미완료 Task 감지, 온보딩 |
| `PreToolUse` | 도구 실행 전 | 검증, 로깅 |
| `PostToolUse` | 도구 실행 후 | 의사결정 감지 |
| `Notification` | 알림 시 | 상태 저장 |
| `Stop` | 세션 종료 시 | 자동 저장 |

## 설정 방법

`~/.claude/settings.json` 또는 프로젝트 `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/session-start.js",
            "timeout": 5000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/detect-decision.sh",
            "timeout": 3000
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/auto-save.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

## 훅 스크립트

### session-start.js

세션 시작 시 실행됩니다.

**기능:**
- 미완료 Task 자동 감지 (`tasks/` 폴더 스캔)
- Workspace 정보 수집 (skills, repos, adapters)
- 세션 시작 배너 출력
- 이어하기 질문 프롬프트 생성

**출력 예시:**
```
┌────────────────────────────────────────────────────────────┐
│  🏠 Workspace: work                                        │
│  ─────────────────────────────────────────────────────────  │
│  📦 Adapters:                                              │
│  ├─ Task Manager: todoist                                  │
│  └─ AI Memory: graphiti                                    │
│  📚 Skills (3): task-manager, pg-webhook, convention       │
│  📂 Repos (2): backend, frontend                           │
│  🤖 Agents: analyzer, implementer, tester, reviewer        │
└────────────────────────────────────────────────────────────┘

🔄 이전 작업 감지됨
| Task | 결제 기능 |
| 유형 | 📦 code |
| 진행 | 2/3 서브태스크 완료 |
| 현재 | 3. 통합 테스트 |
| 마지막 | 2시간 전 |
```

### detect-decision.sh

코드 변경 시 의사결정 패턴을 감지합니다.

```bash
#!/bin/bash
# 의사결정 패턴 감지 (예: TODO, DECISION, 주석 등)
# 감지 시 AI Memory 저장 프롬프트
```

### auto-save.sh

세션 종료 시 자동 저장합니다.

```bash
#!/bin/bash
# 현재 Task 감지
# 미저장 상태가 있으면 history에 기록
```

## Workspace에서 커스텀

각 Workspace에서 `.claude/settings.json`으로 오버라이드:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "hooks/notify-slack.sh"
          }
        ]
      }
    ]
  }
}
```

## 환경변수

| 변수 | 설명 |
|------|------|
| `WORKBENCH_DEBUG=1` | 디버그 로그 활성화 |
| `CLAUDE_PROJECT_ROOT` | 프로젝트 루트 경로 |

## 주의사항

- Hook은 동기 실행 (너무 오래 걸리면 안 됨)
- timeout 설정 권장 (기본 5초)
- 실패해도 메인 작업은 계속됨
- Node.js 필요 (session-start.js)
