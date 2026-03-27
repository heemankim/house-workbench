#!/usr/bin/env node
/**
 * Workbench - Session Start Hook
 *
 * 세션 시작 시 실행되어 다음을 수행합니다:
 * 1. 미완료 Task 자동 감지
 * 2. Workspace 상태 수집
 * 3. 이어하기 질문 생성
 * 4. 세션 시작 배너 출력
 */

const { debugLog } = require('./lib/debug');
const { findWorkspaceRoot } = require('./lib/workspace-resolver');
const { generateSessionStartResponse } = require('./lib/response-generator');

// Main
try {
  const workspaceRoot = findWorkspaceRoot();
  debugLog('SessionStart', 'Workspace root', { path: workspaceRoot });

  const response = generateSessionStartResponse(workspaceRoot);
  console.log(JSON.stringify(response));

} catch (e) {
  debugLog('SessionStart', 'Error', { error: e.message });

  // 에러 시에도 기본 응답
  console.log(JSON.stringify({
    systemMessage: 'Workbench session started',
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      error: e.message
    }
  }));
}

process.exit(0);
