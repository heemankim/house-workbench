/**
 * Session start response generation
 */

const { debugLog } = require('./debug');
const { getWorkspaceInfo } = require('./workspace-info');
const { scanIncompleteTasks } = require('./task-parser');

/**
 * 시간 차이를 읽기 쉬운 형태로 변환
 */
function formatTimeDiff(date) {
  const now = new Date();
  const diff = now - date;

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (days > 0) return `${days}일 전`;
  if (hours > 0) return `${hours}시간 전`;
  if (minutes > 0) return `${minutes}분 전`;
  return '방금 전';
}

/**
 * 세션 시작 응답 생성
 */
function generateSessionStartResponse(workspaceRoot) {
  const workspaceInfo = getWorkspaceInfo(workspaceRoot);
  const incompleteTasks = scanIncompleteTasks(workspaceRoot);

  debugLog('SessionStart', 'Workspace info', workspaceInfo);
  debugLog('SessionStart', 'Incomplete tasks', { count: incompleteTasks.length });

  let additionalContext = '';

  // 세션 시작 배너
  additionalContext += `# Workbench Session Started\n\n`;
  additionalContext += '```\n';
  additionalContext += '┌────────────────────────────────────────────────────────────┐\n';
  additionalContext += `│  🏠 Workspace: ${workspaceInfo.name.padEnd(42)}│\n`;
  additionalContext += '│  ─────────────────────────────────────────────────────────  │\n';
  additionalContext += '│                                                            │\n';
  additionalContext += `│  📦 Adapters:                                              │\n`;
  additionalContext += `│  ├─ Task Manager: ${workspaceInfo.adapters.taskManager.padEnd(38)}│\n`;
  additionalContext += `│  └─ AI Memory: ${workspaceInfo.adapters.aiMemory.padEnd(41)}│\n`;
  additionalContext += '│                                                            │\n';

  if (workspaceInfo.skills.length > 0) {
    additionalContext += `│  📚 Skills (${workspaceInfo.skills.length}):`.padEnd(61) + '│\n';
    additionalContext += `│  └─ ${workspaceInfo.skills.slice(0, 3).join(', ')}${workspaceInfo.skills.length > 3 ? '...' : ''}`.padEnd(57) + '│\n';
  }

  if (workspaceInfo.repos.length > 0) {
    additionalContext += `│  📂 Repos (${workspaceInfo.repos.length}):`.padEnd(61) + '│\n';
    additionalContext += `│  └─ ${workspaceInfo.repos.slice(0, 3).join(', ')}${workspaceInfo.repos.length > 3 ? '...' : ''}`.padEnd(57) + '│\n';
  }

  additionalContext += '│                                                            │\n';
  additionalContext += '│  🤖 Agents: analyzer, checker, implementer, reviewer, tester│\n';
  additionalContext += '│                                                            │\n';
  additionalContext += '│  ─────────────────────────────────────────────────────────  │\n';
  additionalContext += '│  /wb - 도움말 | /wb-status - 상태 | /wb-start - 시작        │\n';
  additionalContext += '└────────────────────────────────────────────────────────────┘\n';
  additionalContext += '```\n\n';

  // 미완료 Task가 있는 경우
  let onboardingPrompt = null;

  if (incompleteTasks.length > 0) {
    const mostRecent = incompleteTasks[0];
    const typeIcon = mostRecent.type === 'ops' ? '🔧' : '📦';
    const timeDiff = formatTimeDiff(mostRecent.lastModified);

    additionalContext += `## 🔄 이전 작업 감지됨\n\n`;
    additionalContext += `| 항목 | 내용 |\n`;
    additionalContext += `|------|------|\n`;
    additionalContext += `| **Task** | ${mostRecent.name} |\n`;
    additionalContext += `| **유형** | ${typeIcon} ${mostRecent.type} |\n`;
    additionalContext += `| **진행** | ${mostRecent.subtaskCompleted}/${mostRecent.subtaskTotal} 서브태스크 완료 |\n`;
    if (mostRecent.currentSubtask) {
      additionalContext += `| **현재** | ${mostRecent.currentSubtask.number}. ${mostRecent.currentSubtask.name} |\n`;
    }
    additionalContext += `| **마지막** | ${timeDiff} |\n`;
    additionalContext += `\n`;

    if (incompleteTasks.length > 1) {
      additionalContext += `> 📋 다른 미완료 Task: ${incompleteTasks.slice(1, 3).map(t => t.name).join(', ')}${incompleteTasks.length > 3 ? ` 외 ${incompleteTasks.length - 3}개` : ''}\n\n`;
    }

    additionalContext += `### 🚨 사용자의 첫 메시지에서 AskUserQuestion 호출 필수\n\n`;

    // 온보딩 질문 생성
    onboardingPrompt = {
      questions: [{
        question: `이전 작업이 감지되었습니다. "${mostRecent.name}" (${mostRecent.type}) - ${mostRecent.subtaskCompleted}/${mostRecent.subtaskTotal} 완료. 어떻게 하시겠습니까?`,
        header: 'Resume',
        options: [
          {
            label: `이어서 작업`,
            description: `${mostRecent.currentSubtask ? mostRecent.currentSubtask.name + ' 진행' : '마지막 서브태스크 이어서'}`
          },
          {
            label: '새 Task 시작',
            description: '새로운 작업 시작 (/wb-start)'
          },
          {
            label: '상태 확인',
            description: '전체 상태 조회 (/wb-status)'
          }
        ],
        multiSelect: false
      }]
    };

    additionalContext += `AskUserQuestion 호출 형식:\n`;
    additionalContext += '```json\n';
    additionalContext += JSON.stringify(onboardingPrompt, null, 2);
    additionalContext += '\n```\n\n';

    additionalContext += `### 선택별 후속 작업:\n`;
    additionalContext += `- **이어서 작업** → \`/wb-resume ${mostRecent.name}\` 실행\n`;
    additionalContext += `- **새 Task 시작** → \`/wb-start\` 실행\n`;
    additionalContext += `- **상태 확인** → \`/wb-status\` 실행\n\n`;

  } else {
    // 미완료 Task 없음
    additionalContext += `## ✨ 새 세션 시작\n\n`;
    additionalContext += `진행 중인 Task가 없습니다.\n\n`;
    additionalContext += `### 시작하기\n`;
    additionalContext += `- \`/wb-start "Task 이름"\` - 새 Task 시작\n`;
    additionalContext += `- \`/wb-status\` - Workspace 상태 확인\n`;
    additionalContext += `- \`/wb\` - 도움말\n\n`;
  }

  // 활용 내역 형식 안내
  additionalContext += `## 📊 활용 내역 표시 규칙\n\n`;
  additionalContext += `모든 /wb-* 커맨드 실행 후 다음 형식으로 사용된 리소스를 표시하세요:\n\n`;
  additionalContext += '```\n';
  additionalContext += '📊 /wb-{command} 실행 완료\n';
  additionalContext += '├─ 📦 Type: {code|ops} (해당 시)\n';
  additionalContext += '├─ 🤖 Agents: {사용된 에이전트}\n';
  additionalContext += '├─ 💾 Memory: {메모리 작업}\n';
  additionalContext += '├─ 📚 Skills: {참조된 스킬}\n';
  additionalContext += '├─ 🔧 Actions: {수행된 작업}\n';
  additionalContext += '└─ ⏱️ 소요: {시간}\n';
  additionalContext += '```\n';

  const response = {
    systemMessage: `Workbench session started (${workspaceInfo.name})`,
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      workspace: workspaceInfo.name,
      hasIncompleteTasks: incompleteTasks.length > 0,
      incompleteTaskCount: incompleteTasks.length,
      mostRecentTask: incompleteTasks[0]?.name || null,
      additionalContext: additionalContext
    }
  };

  return response;
}

module.exports = { formatTimeDiff, generateSessionStartResponse };
