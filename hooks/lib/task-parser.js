/**
 * Task and subtask parsing utilities
 */

const fs = require('fs');
const path = require('path');
const { debugLog } = require('./debug');
const { getVaultDir, resolveTask } = require('./workspace-resolver');

/**
 * 서브태스크 파싱 (체크박스 + 테이블 형식 지원)
 *
 * 체크박스: - [x] 01. 서브태스크 이름
 * 테이블:  | 01 | TICKET-123 | 서브태스크 이름 | ✅ |
 */
function parseSubtasks(content) {
  const subtasks = [];

  // 1. 체크박스 형식: - [x] 01. 이름 (→ [[link]] 등 후행 텍스트 제거)
  for (const match of content.matchAll(/- \[([ x])\] (\d+)\.\s+(.+)/g)) {
    const isComplete = match[1] === 'x';
    const number = parseInt(match[2]);
    const name = match[3].replace(/\s*→\s*\[\[.*?\]\].*$/, '').replace(/\s*[✅⏳].*$/, '').trim();
    subtasks.push({ number, name, isComplete });
  }

  // 2. 테이블 형식 (체크박스가 없을 때만): | 01 | ... | ✅ | 또는 | 01 | ... | ⬜ |
  if (subtasks.length === 0) {
    for (const match of content.matchAll(/\|\s*(\d+)\s*\|[^|]*\|\s*([^|]+?)\s*\|\s*(✅|⬜|❌|⏳)\s*\|/g)) {
      const number = parseInt(match[1]);
      const name = match[2].trim();
      const isComplete = match[3] === '✅';
      subtasks.push({ number, name, isComplete });
    }
  }

  return subtasks;
}

/**
 * 미완료 Task 스캔
 */
function scanIncompleteTasks(workspaceRoot) {
  const tasksDir = path.join(workspaceRoot, 'data', 'tasks');
  const incompleteTasks = [];

  if (!fs.existsSync(tasksDir)) {
    return incompleteTasks;
  }

  try {
    const vaultDir = getVaultDir(workspaceRoot);
    const tasks = fs.readdirSync(tasksDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);

    for (const taskName of tasks) {
      const taskPath = path.join(tasksDir, taskName);
      const taskMdPath = path.join(taskPath, 'TASK.md');

      if (!fs.existsSync(taskMdPath)) continue;

      // vault SSoT 우선, fallback to data/tasks
      const { content, resolvedPath } = resolveTask(workspaceRoot, vaultDir, taskName, taskMdPath);

      // Task 유형 감지 (task_type도 지원)
      const typeMatch = content.match(/(?:task_)?type:\s*(code|ops|research)/i);
      const type = typeMatch ? typeMatch[1].toLowerCase() : 'code';

      // 서브태스크 파싱 (체크박스 + 테이블)
      const subtasks = parseSubtasks(content);
      let completedCount = 0;
      let currentSubtask = null;

      for (const st of subtasks) {
        if (st.isComplete) {
          completedCount++;
        } else if (!currentSubtask) {
          currentSubtask = { number: st.number, name: st.name };
        }
      }

      // 서브태스크가 없거나 전체 완료면 스킵
      if (subtasks.length === 0 || completedCount >= subtasks.length) continue;

      const stat = fs.statSync(resolvedPath);
      const lastModified = stat.mtime;

      incompleteTasks.push({
        name: taskName,
        type,
        subtaskTotal: subtasks.length,
        subtaskCompleted: completedCount,
        currentSubtask,
        lastModified,
        path: taskPath
      });
    }

    // 마지막 수정 시간 기준 정렬 (최신 먼저)
    incompleteTasks.sort((a, b) => b.lastModified - a.lastModified);

  } catch (e) {
    debugLog('SessionStart', 'Task scan error', { error: e.message });
  }

  return incompleteTasks;
}

module.exports = { parseSubtasks, scanIncompleteTasks };
