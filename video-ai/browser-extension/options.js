/**
 * Video-AI Browser Extension - Options Script
 * 处理设置页面的配置管理
 */

// ============================================
// 常量
// ============================================

const DEFAULT_SETTINGS = {
  apiToken: '',
  userId: '',
  interests: 'AI, 编程, 技术',
  outputLength: 'medium',
  language: 'zh-CN',
  autoDownload: false,
  enableNotifications: true,
  saveHistory: true,
  cacheDays: 30
};

// ============================================
// 初始化
// ============================================

/**
 * 页面加载时初始化
 */
document.addEventListener('DOMContentLoaded', () => {
  initializeUI();
  loadSettings();
  setupEventListeners();

  // 检查是否从欢迎流程来
  const params = new URLSearchParams(window.location.search);
  if (params.get('welcome')) {
    document.getElementById('welcomeMessage').classList.remove('hidden');
  }
});

/**
 * 初始化 UI
 */
function initializeUI() {
  // 设置版本号
  const manifest = chrome.runtime.getManifest();
  document.getElementById('version').textContent = manifest.version;
}

// ============================================
// 设置管理
// ============================================

/**
 * 加载设置
 */
async function loadSettings() {
  const settings = await getSettings();

  document.getElementById('apiToken').value = settings.apiToken || '';
  document.getElementById('userId').value = settings.userId || '';
  document.getElementById('interests').value = settings.interests || DEFAULT_SETTINGS.interests;
  document.getElementById('outputLength').value = settings.outputLength || 'medium';
  document.getElementById('language').value = settings.language || 'zh-CN';
  document.getElementById('autoDownload').checked = settings.autoDownload || false;
  document.getElementById('enableNotifications').checked = settings.enableNotifications !== false;
  document.getElementById('saveHistory').checked = settings.saveHistory !== false;
  document.getElementById('cacheDays').value = settings.cacheDays || 30;
}

/**
 * 获取所有设置
 */
async function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(DEFAULT_SETTINGS, (data) => {
      resolve(data);
    });
  });
}

/**
 * 保存设置
 */
async function saveSettings() {
  const settings = {
    apiToken: document.getElementById('apiToken').value.trim(),
    userId: document.getElementById('userId').value.trim(),
    interests: document.getElementById('interests').value.trim(),
    outputLength: document.getElementById('outputLength').value,
    language: document.getElementById('language').value,
    autoDownload: document.getElementById('autoDownload').checked,
    enableNotifications: document.getElementById('enableNotifications').checked,
    saveHistory: document.getElementById('saveHistory').checked,
    cacheDays: parseInt(document.getElementById('cacheDays').value) || 30
  };

  return new Promise((resolve) => {
    chrome.storage.sync.set(settings, () => {
      showSaveStatus('✅ 设置已保存');
      resolve();
    });
  });
}

/**
 * 恢复默认设置
 */
async function resetSettings() {
  if (confirm('确定要恢复所有设置到默认值吗？')) {
    await chrome.storage.sync.clear();
    await chrome.storage.sync.set(DEFAULT_SETTINGS);
    await loadSettings();
    showSaveStatus('✅ 已恢复默认设置');
  }
}

// ============================================
// 功能函数
// ============================================

/**
 * 测试 API 连接
 */
async function testConnection() {
  const apiToken = document.getElementById('apiToken').value.trim();

  if (!apiToken) {
    showConnectionStatus('❌ 请先输入 API Token', 'error');
    return;
  }

  const statusEl = document.getElementById('connectionStatus');
  statusEl.innerHTML = '<span class="loading">⏳ 测试中...</span>';
  statusEl.classList.remove('hidden');

  try {
    const response = await fetch(
      'https://api.video-ai.com/api/v1/auth/verify',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiToken}`
        }
      }
    );

    if (response.ok) {
      const data = await response.json();

      // 保存用户 ID
      document.getElementById('userId').value = data.user_id || '';
      await chrome.storage.sync.set({ userId: data.user_id });

      showConnectionStatus(
        `✅ 连接成功！欢迎，${data.user_name || '用户'}`,
        'success'
      );
    } else {
      showConnectionStatus('❌ Token 无效或已过期', 'error');
    }
  } catch (error) {
    showConnectionStatus(
      `❌ 连接失败: ${error.message}`,
      'error'
    );
  }
}

/**
 * 清除缓存
 */
async function clearCache() {
  if (confirm('确定要清除所有缓存数据吗？')) {
    try {
      // 清除本地存储中的缓存
      await chrome.storage.local.clear();

      showCacheStatus('✅ 缓存已清除');
    } catch (error) {
      showCacheStatus(`❌ 清除失败: ${error.message}`, 'error');
    }
  }
}

/**
 * 导出设置
 */
async function exportSettings() {
  try {
    const settings = await getSettings();

    // 创建 JSON 文件
    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    // 下载文件
    const link = document.createElement('a');
    link.href = url;
    link.download = `video-ai-settings-${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showSaveStatus('✅ 设置已导出');
  } catch (error) {
    showSaveStatus(`❌ 导出失败: ${error.message}`, 'error');
  }
}

/**
 * 导入设置
 */
function importSettings() {
  document.getElementById('importFile').click();
}

/**
 * 处理导入的文件
 */
async function handleImportFile(event) {
  const file = event.target.files[0];

  if (!file) {
    return;
  }

  try {
    const content = await file.text();
    const settings = JSON.parse(content);

    // 验证设置
    if (!settings.apiToken) {
      showSaveStatus('⚠️ 导入的设置文件不完整', 'warning');
      return;
    }

    // 导入设置
    await chrome.storage.sync.set(settings);
    await loadSettings();

    showSaveStatus('✅ 设置已导入');
  } catch (error) {
    showSaveStatus(
      `❌ 导入失败: ${error.message}`,
      'error'
    );
  }
}

// ============================================
// UI 反馈
// ============================================

/**
 * 显示保存状态
 */
function showSaveStatus(message, type = 'success') {
  const statusEl = document.getElementById('saveStatus');

  statusEl.textContent = message;
  statusEl.className = `save-status ${type}`;
  statusEl.classList.remove('hidden');

  setTimeout(() => {
    statusEl.classList.add('hidden');
  }, 3000);
}

/**
 * 显示连接状态
 */
function showConnectionStatus(message, type = 'success') {
  const statusEl = document.getElementById('connectionStatus');

  statusEl.innerHTML = `<span class="${type}">${message}</span>`;
  statusEl.classList.remove('hidden');

  if (type === 'success') {
    setTimeout(() => {
      statusEl.classList.add('hidden');
    }, 5000);
  }
}

/**
 * 显示缓存状态
 */
function showCacheStatus(message, type = 'success') {
  const statusEl = document.getElementById('cacheStatus');

  statusEl.textContent = message;
  statusEl.className = `cache-status ${type}`;
  statusEl.classList.remove('hidden');

  if (type === 'success') {
    setTimeout(() => {
      statusEl.classList.add('hidden');
    }, 3000);
  }
}

// ============================================
// 事件监听
// ============================================

/**
 * 设置事件监听
 */
function setupEventListeners() {
  // 标签页导航
  document.querySelectorAll('.nav-item').forEach((item) => {
    item.addEventListener('click', () => {
      const tabName = item.getAttribute('data-tab');
      switchTab(tabName);
    });
  });

  // 按钮事件
  document.getElementById('saveBtn').addEventListener('click', saveSettings);
  document.getElementById('resetBtn').addEventListener('click', resetSettings);
  document.getElementById('testConnectionBtn').addEventListener('click', testConnection);
  document.getElementById('clearCacheBtn').addEventListener('click', clearCache);
  document.getElementById('exportSettingsBtn').addEventListener('click', exportSettings);
  document.getElementById('importSettingsBtn').addEventListener('click', importSettings);
  document.getElementById('importFile').addEventListener('change', handleImportFile);

  // API Token 输入框变化时显示提示
  document.getElementById('apiToken').addEventListener('input', () => {
    document.getElementById('connectionStatus').classList.add('hidden');
  });
}

/**
 * 切换标签页
 */
function switchTab(tabName) {
  // 隐藏所有标签页
  document.querySelectorAll('.tab-content').forEach((tab) => {
    tab.classList.add('hidden');
  });

  // 移除所有导航项的活跃状态
  document.querySelectorAll('.nav-item').forEach((item) => {
    item.classList.remove('active');
  });

  // 显示选中的标签页
  const selectedTab = document.getElementById(`${tabName}Tab`);
  if (selectedTab) {
    selectedTab.classList.remove('hidden');
  }

  // 标记导航项为活跃
  document
    .querySelector(`[data-tab="${tabName}"]`)
    ?.classList.add('active');
}

console.log('Video-AI options script loaded');
