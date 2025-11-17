/**
 * Video-AI Browser Extension - Content Script
 * 在 YouTube 页面中注入功能和快捷按钮
 */

// ============================================
// YouTube 页面集成
// ============================================

/**
 * 在 YouTube 控制栏中添加 Video-AI 按钮
 */
function addVideoAIButton() {
  // 防止重复添加
  if (document.getElementById('videoai-btn')) {
    return;
  }

  // 获取 YouTube 播放器控制栏
  const controls = document.querySelector('.ytp-right-controls');

  if (!controls) {
    // 如果控制栏不存在，稍后重试
    setTimeout(addVideoAIButton, 1000);
    return;
  }

  // 创建按钮
  const button = document.createElement('button');
  button.id = 'videoai-btn';
  button.className = 'ytp-button';
  button.title = 'Video-AI - 智能视频编辑';
  button.innerHTML = '<svg width="100%" height="100%" viewBox="0 0 24 24" fill="currentColor"><text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" font-size="14" font-weight="bold">🎯</text></svg>';

  // 应用样式
  button.style.cssText = `
    cursor: pointer;
    display: inline-block;
    background: none;
    border: none;
    color: #fff;
    padding: 0 6px;
    height: 100%;
    line-height: 100%;
    font-size: 18px;
  `;

  // 事件监听
  button.addEventListener('click', handleButtonClick);
  button.addEventListener('mouseenter', () => {
    button.style.opacity = '0.8';
  });
  button.addEventListener('mouseleave', () => {
    button.style.opacity = '1';
  });

  // 在控制栏的最右边插入按钮
  controls.appendChild(button);
}

/**
 * 处理按钮点击
 */
function handleButtonClick() {
  // 打开插件弹出窗口
  chrome.runtime.sendMessage(
    { action: 'openPopup' },
    (response) => {
      if (chrome.runtime.lastError) {
        console.error('发送消息失败:', chrome.runtime.lastError);
      }
    }
  );
}

/**
 * 获取当前视频信息
 */
function getVideoInfo() {
  try {
    // 获取视频标题
    const titleElement = document.querySelector('h1.title yt-formatted-string');
    const title = titleElement?.textContent || '';

    // 获取视频时长
    const durationElement = document.querySelector('ytd-video-primary-info-renderer span.style-scope.yt-formatted-string');
    const duration = durationElement?.textContent || '';

    // 获取视频描述
    const descElement = document.querySelector('yt-formatted-string[name="description"]');
    const description = descElement?.textContent || '';

    return {
      title: title.trim(),
      duration: duration.trim(),
      description: description.trim()
    };
  } catch (error) {
    console.error('获取视频信息失败:', error);
    return {
      title: '',
      duration: '',
      description: ''
    };
  }
}

// ============================================
// 消息处理
// ============================================

/**
 * 监听来自 popup 的消息
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getVideoInfo') {
    const info = getVideoInfo();
    sendResponse(info);
  }
});

// ============================================
// YouTube SPA 页面导航处理
// ============================================

/**
 * 监听 YouTube 页面变化（YouTube 是单页应用）
 * 当用户点击不同视频时，添加新的按钮
 */
let lastUrl = location.href;

const observer = new MutationObserver(() => {
  const url = location.href;

  // 检查 URL 是否改变（用于 YouTube 的历史状态变化）
  if (url !== lastUrl) {
    lastUrl = url;

    // 检查是否为视频页面
    if (/youtube\.com\/watch/.test(url) || /youtu\.be\//.test(url)) {
      // 延迟添加按钮，等待页面完全加载
      setTimeout(addVideoAIButton, 1000);
    }
  }

  // 定期检查按钮是否存在
  if (!document.getElementById('videoai-btn')) {
    if (/youtube\.com\/watch/.test(location.href) || /youtu\.be\//.test(location.href)) {
      addVideoAIButton();
    }
  }
});

// 配置观察者选项
const observerOptions = {
  subtree: true,
  childList: true,
  attributes: false,
  attributeOldValue: false,
  characterData: false
};

// 开始观察页面变化
observer.observe(document.documentElement, observerOptions);

// ============================================
// 初始化
// ============================================

/**
 * 当脚本加载时立即检查是否需要添加按钮
 */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (/youtube\.com\/watch/.test(location.href) || /youtu\.be\//.test(location.href)) {
      setTimeout(addVideoAIButton, 1000);
    }
  });
} else {
  // DOM 已加载
  if (/youtube\.com\/watch/.test(location.href) || /youtu\.be\//.test(location.href)) {
    setTimeout(addVideoAIButton, 1000);
  }
}

console.log('Video-AI content script loaded');
