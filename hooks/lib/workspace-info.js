/**
 * Workspace information collection
 */

const fs = require('fs');
const path = require('path');

/**
 * Workspace 정보 수집
 */
function getWorkspaceInfo(workspaceRoot) {
  const info = {
    name: path.basename(workspaceRoot),
    skills: [],
    repos: [],
    adapters: {
      taskManager: 'local',
      aiMemory: 'local'
    }
  };

  // Skills 스캔 (.claude/skills/ 우선, 없으면 skills/ fallback)
  // 폴더 구조 (skills/{name}/SKILL.md) 및 레거시 플랫 구조 (skills/{name}.md) 모두 지원
  const claudeSkillsDir = path.join(workspaceRoot, '.claude', 'skills');
  const legacySkillsDir = path.join(workspaceRoot, 'skills');
  const skillsDir = fs.existsSync(claudeSkillsDir) ? claudeSkillsDir : legacySkillsDir;
  if (fs.existsSync(skillsDir)) {
    try {
      const entries = fs.readdirSync(skillsDir, { withFileTypes: true });
      const skills = [];
      for (const entry of entries) {
        if (entry.isDirectory()) {
          const skillFile = path.join(skillsDir, entry.name, 'SKILL.md');
          if (fs.existsSync(skillFile)) {
            skills.push(entry.name);
          }
        } else if (entry.isFile() && entry.name.endsWith('.md')) {
          skills.push(entry.name.replace('.md', ''));
        }
      }
      info.skills = skills;
    } catch (e) {}
  }

  // Repos 스캔
  const reposJsonPath = path.join(workspaceRoot, 'repos.json');
  if (fs.existsSync(reposJsonPath)) {
    try {
      const reposJson = JSON.parse(fs.readFileSync(reposJsonPath, 'utf8'));
      info.repos = (reposJson.repos || []).map(r => r.name);
    } catch (e) {}
  }

  // Config 읽기
  const configPath = path.join(workspaceRoot, 'config.json');
  if (fs.existsSync(configPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      if (config.adapters) {
        info.adapters.taskManager = config.adapters.taskManager?.type || 'local';
        info.adapters.aiMemory = config.adapters.aiMemory?.type || 'local';
      }
    } catch (e) {}
  }

  return info;
}

module.exports = { getWorkspaceInfo };
