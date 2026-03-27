/**
 * Debug logging utility
 */

const DEBUG = process.env.WORKBENCH_DEBUG === '1';

function debugLog(category, message, data = {}) {
  if (DEBUG) {
    console.error(`[WB:${category}] ${message}`, JSON.stringify(data));
  }
}

module.exports = { debugLog };
