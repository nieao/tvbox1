/**
 * Video-AI Browser Extension - Popup Script
 * 处理弹出页面的用户交互和 API 调用
 */

// 常量
const CONFIG = {
  API_BASE_URL: 'https://api.video-ai.com/api/v1',
  POLL_INTERVAL: 2000,
  REQUEST_TIMEOUT: 30000
};

// ============================================
// 视频信息处理
// ============================================

/**
 * 获取当前标签页的 YouTube 视频信息
 */
async function getCurrentVideo() {
  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true
    });

    if (!tab.url) {
      return null;
    }

    // 检查是否为 YouTube 视频页面
    const isYouTubeVideo = /youtube\.com\/watch/.test(tab.url) || /youtu\.be\//.test(tab.url);

    if (!isYouTubeVideo) {
      return null;
    }

    // 提取视频 ID
    let videoId = null;
    const url = new URL(tab.url);

    if (url.hostname.includes('youtube.com')) {
      videoId = url.searchParams.get('v');
    } else if (url.hostname.includes('youtu.be')) {
      videoId = url.pathname.split('/')[1];
    }

    if (!videoId) {
      return null;
    }

    // 获取视频标题
    const response = await chrome.tabs.sendMessage(tab.id, {
      action: 'getVideoInfo'
    }).catch(() => null);

    return {
      videoId,
      videoUrl: tab.url,
      videoTitle: response?.title || `视频 ${videoId}`,
      tabId: tab.id
    };
  } catch (error) {
    console.error('获取视频信息失败:', error);
    return null;
  }
}

/**
 * 更新 UI 显示视频信息
 */
async function updateVideoInfo() {
  const video = await getCurrentVideo();
  const statusEl = document.getElementById('videoStatus');
  const actionSection = document.getElementById('actionSection');

  if (video) {
    statusEl.innerHTML = `
      <div class="video-details">
        <div class="video-title">${escapeHtml(video.videoTitle)}</div>
        <div class="video-id">ID: ${video.videoId}</div>
      </div>
    `;
    actionSection.classList.remove('hidden');
  } else {
    statusEl.innerHTML = '❌ 请在 YouTube 视频页面使用此功能';
    statusEl.style.color = '#d32f2f';
    actionSection.classList.add('hidden');
  }
}

// ============================================
// 处理和 API 调用
// ============================================

/**
 * 处理视频
 */
async function processVideo() {
  const video = await getCurrentVideo();

  if (!video) {
    showError('请在 YouTube 视频页面使用此功能');
    return;
  }

  // 禁用按钮
  const processBtn = document.getElementById('processBtn');
  processBtn.disabled = true;

  try {
    // 获取用户设置
    const settings = await getSettings();
    const interests = (settings.interests || '')
      .split(',')
      .map(t => t.trim())
      .filter(t => t);

    // 验证配置
    if (!settings.apiToken) {
      showError('❌ 请先配置 API Token，点击"更多设置"进行配置');
      processBtn.disabled = false;
      return;
    }

    // 显示进度
    showProgress('正在初始化处理...');

    // 调用 API 开始处理
    const jobId = await startProcessing(video, interests, settings);

    // 轮询任务状态
    await pollJobStatus(jobId, settings.apiToken);

  } catch (error) {
    showError(`❌ 处理失败: ${error.message}`);
    processBtn.disabled = false;
  }
}

/**
 * 启动视频处理
 */
async function startProcessing(video, interests, settings) {
  const response = await fetchWithTimeout(
    `${CONFIG.API_BASE_URL}/videos/process`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${settings.apiToken}`
      },
      body: JSON.stringify({
        video_url: video.videoUrl,
        user_interests: interests,
        output_length: settings.outputLength || 'medium'
      })
    },
    CONFIG.REQUEST_TIMEOUT
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `API 错误: ${response.status}`);
  }

  const result = await response.json();

  if (!result.job_id) {
    throw new Error('未获得任务 ID');
  }

  return result.job_id;
}

/**
 * 轮询任务状态
 */
async function pollJobStatus(jobId, apiToken) {
  let attempts = 0;
  const maxAttempts = 180; // 6 小时（每次轮询间隔 2 秒）

  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      attempts++;

      if (attempts > maxAttempts) {
        clearInterval(interval);
        reject(new Error('任务超时，请稍后查看'));
        return;
      }

      try {
        const response = await fetchWithTimeout(
          `${CONFIG.API_BASE_URL}/jobs/${jobId}`,
          {
            headers: {
              'Authorization': `Bearer ${apiToken}`
            }
          },
          CONFIG.REQUEST_TIMEOUT
        );

        if (!response.ok) {
          throw new Error(`查询失败: ${response.status}`);
        }

        const status = await response.json();
        updateProgress(status.progress || 0, status.current_step);

        if (status.status === 'completed') {
          clearInterval(interval);
          showSuccess(status.result);
          resolve(status.result);
        } else if (status.status === 'failed') {
          clearInterval(interval);
          reject(new Error(status.error_message || '处理失败'));
        }
      } catch (error) {
        console.error('轮询失败:', error);
        // 继续轮询，避免网络波动导致失败
      }
    }, CONFIG.POLL_INTERVAL);
  });
}

// ============================================
// 设置管理
// ============================================

/**
 * 获取用户设置
 */
async function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(
      {
        apiToken: '',
        interests: 'AI, 编程, 技术',
        outputLength: 'medium',
        autoDownload: false
      },
      resolve
    );
  });
}

/**
 * 保存用户设置
 */
async function saveSettings(settings) {
  return new Promise((resolve) => {
    chrome.storage.sync.set(settings, resolve);
  });
}

/**
 * 初始化 UI 中的设置
 */
async function initializeSettings() {
  const settings = await getSettings();

  document.getElementById('interests').value = settings.interests || '';
  document.getElementById('outputLength').value = settings.outputLength || 'medium';
  document.getElementById('autoDownload').checked = settings.autoDownload || false;
}

/**
 * 保存当前 UI 中的设置
 */
async function saveCurrentSettings() {
  const settings = {
    interests: document.getElementById('interests').value,
    outputLength: document.getElementById('outputLength').value,
    autoDownload: document.getElementById('autoDownload').checked
  };

  await saveSettings(settings);
}

// ============================================
// UI 反馈
// ============================================

/**
 * 显示进度
 */
function showProgress(message = '处理中...') {
  const progressEl = document.getElementById('progress');
  const statusEl = document.getElementById('status');

  document.getElementById('progressLabel').textContent = message;
  document.getElementById('progressText').textContent = '0%';
  document.getElementById('progressFill').style.width = '0%';

  progressEl.classList.remove('hidden');
  statusEl.classList.add('hidden');
}

/**
 * 更新进度
 */
function updateProgress(percent, step = '') {
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');
  const progressDetails = document.getElementById('progressDetails');

  progressFill.style.width = Math.min(percent, 100) + '%';
  progressText.textContent = Math.min(Math.floor(percent), 100) + '%';

  if (step) {
    progressDetails.textContent = `当前步骤: ${step}`;
  }
}

/**
 * 显示成功信息
 */
function showSuccess(result) {
  const statusEl = document.getElementById('status');
  const progressEl = document.getElementById('progress');

  let html = `
    <div class="success-message">
      <div class="success-icon">✅</div>
      <div class="success-content">
        <h4>处理完成！</h4>
  `;

  if (result.video_url) {
    html += `
      <p class="success-description">您的视频已准备好</p>
      <a href="${result.video_url}" target="_blank" class="btn btn-success">
        📥 下载视频
      </a>
    `;
  }

  if (result.stats) {
    html += `
      <div class="stats-info">
        <p>原始时长: ${result.stats.original_duration}s</p>
        <p>编辑后: ${result.stats.edited_duration}s</p>
        <p>保留率: ${result.stats.retention_rate}%</p>
      </div>
    `;
  }

  html += '</div></div>';
  statusEl.innerHTML = html;

  progressEl.classList.add('hidden');
  statusEl.classList.remove('hidden');

  // 重新启用按钮
  document.getElementById('processBtn').disabled = false;
}

/**
 * 显示错误信息
 */
function showError(message) {
  const statusEl = document.getElementById('status');
  const progressEl = document.getElementById('progress');

  statusEl.innerHTML = `
    <div class="error-message">
      <div class="error-icon">⚠️</div>
      <div class="error-content">
        <p>${escapeHtml(message)}</p>
      </div>
    </div>
  `;

  progressEl.classList.add('hidden');
  statusEl.classList.remove('hidden');

  // 重新启用按钮
  document.getElementById('processBtn').disabled = false;
}

// ============================================
// 工具函数
// ============================================

/**
 * 带超时的 fetch
 */
function fetchWithTimeout(url, options = {}, timeout = CONFIG.REQUEST_TIMEOUT) {
  return Promise.race([
    fetch(url, options),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('请求超时')), timeout)
    )
  ]);
}

/**
 * 转义 HTML
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ============================================
// 事件监听
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
  // 初始化 UI
  await updateVideoInfo();
  await initializeSettings();

  // 事件监听
  document.getElementById('processBtn').addEventListener('click', processVideo);

  document.getElementById('settingsBtn').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });

  document.getElementById('supportLink').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({
      url: 'https://github.com/your-repo/wiki/help'
    });
  });

  document.getElementById('feedbackLink').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({
      url: 'https://github.com/your-repo/issues'
    });
  });

  // 输入框失焦时保存设置
  document.getElementById('interests').addEventListener('blur', saveCurrentSettings);
  document.getElementById('outputLength').addEventListener('change', saveCurrentSettings);
  document.getElementById('autoDownload').addEventListener('change', saveCurrentSettings);
});
