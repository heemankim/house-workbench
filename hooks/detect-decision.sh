#!/bin/bash
# detect-decision.sh
# 코드 변경에서 의사결정 패턴을 감지합니다.
# 트리거: PostToolUse (Edit|Write)

# 환경 변수로 전달되는 정보
# $CLAUDE_TOOL_NAME: 사용된 도구 이름 (Edit, Write 등)
# $CLAUDE_TOOL_INPUT: 도구 입력 (JSON - file_path, old_string, new_string 등)

# 의사결정 패턴 (주석, TODO 등)
DECISION_PATTERNS=(
    "DECISION:"
    "결정:"
    "선택:"
    "TODO:"
    "FIXME:"
    "NOTE:"
)

# 도구 입력에서 new_string(Edit) 또는 content(Write) 추출
CONTENT=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('new_string', '') or data.get('content', ''))
except:
    pass
" 2>/dev/null)

# 추출 실패 시 종료
if [ -z "$CONTENT" ]; then
    exit 0
fi

# 변경된 코드 내용에서 패턴 검색
for pattern in "${DECISION_PATTERNS[@]}"; do
    if echo "$CONTENT" | grep -q "$pattern"; then
        echo "🔔 의사결정 감지: $pattern"
        touch /tmp/workbench_decision_detected
        exit 0
    fi
done

exit 0
