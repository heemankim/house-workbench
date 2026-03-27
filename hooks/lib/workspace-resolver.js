/**
 * Workspace root discovery and task resolution
 */

const fs = require('fs');
const path = require('path');
const { debugLog } = require('./debug');

/**
 * Workspace 루트 경로 찾기
 */
function findWorkspaceRoot() {
  let dir = process.cwd();

  // config.json 또는 repos.json이 있는 디렉토리 찾기
  while (dir !== path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, 'config.json')) ||
        fs.existsSync(path.join(dir, 'repos.json'))) {
      return dir;
    }
    dir = path.dirname(dir);
  }

  return process.cwd();
}

/**
 * config.json에서 vault 경로 읽기
 */
function getVaultDir(workspaceRoot) {
  const configPath = path.join(workspaceRoot, 'config.json');
  if (fs.existsSync(configPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      if (config.vault) return config.vault;
    } catch (e) {}
  }
  return null;
}

/**
 * Task의 SSoT TASK.md 결정
 * 우선순위: vaultPath → fallback vault/1-Projects/{taskName} → data/tasks
 * @returns {{ content: string, resolvedPath: string }}
 */
function resolveTask(workspaceRoot, vaultDir, taskName, dataTaskMdPath) {
  const dataContent = fs.readFileSync(dataTaskMdPath, 'utf8');

  if (!vaultDir) {
    debugLog('SessionStart', 'No vault configured, using data/tasks', { taskName });
    return { content: dataContent, resolvedPath: dataTaskMdPath };
  }

  // 1. data/tasks TASK.md에서 vaultPath 추출
  const vaultPathMatch = dataContent.match(/vaultPath:\s*"?([^"\n]+)"?/);

  const vaultTaskMd = vaultPathMatch
    ? path.join(workspaceRoot, vaultDir, vaultPathMatch[1], 'TASK.md')
    : path.join(workspaceRoot, vaultDir, '1-Projects', taskName, 'TASK.md');

  if (fs.existsSync(vaultTaskMd)) {
    debugLog('SessionStart', 'Using vault TASK.md', { taskName, path: vaultTaskMd });
    return { content: fs.readFileSync(vaultTaskMd, 'utf8'), resolvedPath: vaultTaskMd };
  }

  debugLog('SessionStart', 'Vault TASK.md not found, fallback to data/tasks', { taskName, tried: vaultTaskMd });
  return { content: dataContent, resolvedPath: dataTaskMdPath };
}

module.exports = { findWorkspaceRoot, getVaultDir, resolveTask };
