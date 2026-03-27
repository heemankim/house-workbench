#!/bin/bash
# auto-save.sh
# 세션 종료 시 자동 저장합니다.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
TASKS_DIR="$PROJECT_DIR/data/tasks"

# data/tasks 디렉토리 없으면 종료
if [ ! -d "$TASKS_DIR" ]; then
    exit 0
fi

# 가장 최근 수정된 TASK.md 찾기
LATEST_TASK=$(find "$TASKS_DIR" -maxdepth 2 -name "TASK.md" -exec stat -f '%m %N' {} \; 2>/dev/null | sort -rn | head -1 | awk '{print $2}')

if [ -z "$LATEST_TASK" ]; then
    exit 0
fi

# TASK.md 경로에서 task 이름 추출
TASK_DIR=$(echo "$LATEST_TASK" | sed "s|$TASKS_DIR/\([^/]*\)/.*|\1|")

if [ -z "$TASK_DIR" ]; then
    exit 0
fi

# 히스토리 파일 경로
HISTORY_DIR="$TASKS_DIR/$TASK_DIR/history"
TODAY=$(date +%Y-%m-%d)
HISTORY_FILE="$HISTORY_DIR/$TODAY.md"

# 히스토리 디렉토리 확인
if [ ! -d "$HISTORY_DIR" ]; then
    exit 0
fi

# 자동 저장 기록 추가
NOW=$(date +%H:%M)
echo "" >> "$HISTORY_FILE"
echo "### 세션 종료 - $NOW" >> "$HISTORY_FILE"
echo "" >> "$HISTORY_FILE"
echo "자동 저장됨." >> "$HISTORY_FILE"

# FTS5 인덱스 비동기 갱신 (세션 종료 시 자동 실행)
CONFIG_FILE="$PROJECT_DIR/config.json"
if [ -f "$CONFIG_FILE" ]; then
    FTS_ENABLED=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('beta',{}).get('fts-indexer',False))" 2>/dev/null)
    if [ "$FTS_ENABLED" = "True" ]; then
        VAULT_REL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('vault','obsidian'))" 2>/dev/null)
        VAULT_PATH="$PROJECT_DIR/$VAULT_REL"
        TOOL_PATH="${CLAUDE_PLUGIN_ROOT:-$PROJECT_DIR}/tools/vault-search.py"
        if [ -d "$VAULT_PATH" ] && [ -f "$TOOL_PATH" ]; then
            python3 "$TOOL_PATH" index --vault "$VAULT_PATH" >/dev/null 2>&1 &
            disown 2>/dev/null
        fi
    fi
fi

echo "✅ 자동 저장 완료: $TASK_DIR"
exit 0
