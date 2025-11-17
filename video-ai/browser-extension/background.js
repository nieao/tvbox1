/**
 * Video-AI Browser Extension - Service Worker (Background)
 * 处理后台任务和消息转发
 */

// ============================================
// 常量
// ============================================

const STORAGE_KEYS = {
  API_TOKEN: 'apiToken',
  USER_ID: 'userId',
  LAST_SYNC: 'lastSync'
};

const ALARM_NAMES = {
  SYNC_SETTINGS: 'syncSettings',
  CHECK_JOBS: 'checkJobs'
};

// ============================================
// 安装和初始化
// ============================================

/**
 * 插件安装时的初始化
 */
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // 打开欢迎页面
    chrome.tabs.create({
      url: chrome.runtime.getURL('options.html?welcome=true')
    });

    // 初始化存储
    chrome.storage.sync.set({
      apiToken: '',
      interests: 'AI, 编程, 技术',
      outputLength: 'medium',
      autoDownload: false
    });
  } else if (details.reason === 'update') {
    // 检查版本更新
    console.log('Extension updated');
  }
});

// ============================================
// 消息处理
// ============================================

/**
 * 监听来自 content scripts 和 popup 的消息
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'openPopup') {
    // 打开选项页面或显示某种反馈
    handleOpenPopup();
    sendResponse({ success: true });
  } else if (request.action === 'getApiToken') {
    // 获取 API Token
    chrome.storage.sync.get(STORAGE_KEYS.API_TOKEN, (data) => {
      sendResponse({ token: data[STORAGE_KEYS.API_TOKEN] || '' });
    });
    return true; // 保持消息通道开放
  } else if (request.action === 'saveSettings') {
    // 保存设置
    chrome.storage.sync.set(request.settings, () => {
      sendResponse({ success: true });
    });
    return true;
  } else if (request.action === 'getSettings') {
    // 获取设置
    chrome.storage.sync.get(null, (data) => {
      sendResponse({ settings: data });
    });
    return true;
  }
});

// ============================================
// 辅助函数
// ============================================

/**
 * 打开弹出页面
 */
function handleOpenPopup() {
  // 在 Manifest V3 中，我们不能直接打开弹出页面
  // 但我们可以显示页面操作或打开 options 页面
  chrome.action.openPopup().catch((error) => {
    console.log('Opening action popup failed, redirecting to options:', error);
    chrome.runtime.openOptionsPage();
  });
}

/**
 * 获取当前活跃标签页
 */
async function getCurrentTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  return tabs[0];
}

/**
 * 注入内容脚本到标签页
 */
async function injectContentScript(tabId) {
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ['content.js']
    });
  } catch (error) {
    console.error('Failed to inject content script:', error);
  }
}

// ============================================
// 定时任务
// ============================================

/**
 * 创建或更新定时任务
 */
function setupAlarms() {
  // 每小时同步一次设置
  chrome.alarms.create(ALARM_NAMES.SYNC_SETTINGS, {
    periodInMinutes: 60
  });

  // 每 5 分钟检查一次待处理的任务
  chrome.alarms.create(ALARM_NAMES.CHECK_JOBS, {
    periodInMinutes: 5
  });
}

/**
 * 监听定时任务触发
 */
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === ALARM_NAMES.SYNC_SETTINGS) {
    syncSettings();
  } else if (alarm.name === ALARM_NAMES.CHECK_JOBS) {
    checkPendingJobs();
  }
});

/**
 * 同步设置
 */
async function syncSettings() {
  try {
    const data = await chrome.storage.sync.get(STORAGE_KEYS.API_TOKEN);
    const token = data[STORAGE_KEYS.API_TOKEN];

    if (!token) {
      console.log('No API token configured');
      return;
    }

    // 可以在这里添加与服务器的同步逻辑
    console.log('Settings synced');
  } catch (error) {
    console.error('Settings sync failed:', error);
  }
}

/**
 * 检查待处理的任务
 */
async function checkPendingJobs() {
  try {
    // 检查本地存储中是否有待处理的任务
    const data = await chrome.storage.local.get('pendingJobs');
    const pendingJobs = data.pendingJobs || [];

    if (pendingJobs.length === 0) {
      return;
    }

    console.log(`Checking ${pendingJobs.length} pending jobs`);

    // 可以在这里添加与 API 的交互逻辑
    // 查询每个任务的状态
  } catch (error) {
    console.error('Pending jobs check failed:', error);
  }
}

// ============================================
// 启动
// ============================================

// 启动时设置定时任务
setupAlarms();

console.log('Video-AI background service worker loaded');
