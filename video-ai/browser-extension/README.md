# Video-AI 浏览器扩展

> 一键智能剪辑 YouTube 视频，实现个性化内容推荐和自动视频编辑

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Browsers](https://img.shields.io/badge/browsers-Chrome%20%7C%20Firefox%20%7C%20Edge-blue.svg)

## 目录

- [功能特性](#功能特性)
- [安装指南](#安装指南)
  - [Chrome](#chrome)
  - [Firefox](#firefox)
  - [Edge](#edge)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [配置选项](#配置选项)
- [API 配置](#api-配置)
- [开发指南](#开发指南)
- [项目结构](#项目结构)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 功能特性

### 核心功能

✅ **一键智能剪辑**
- 在 YouTube 页面直接对视频进行智能剪辑
- 基于用户兴趣自动识别关键片段
- 支持多种输出长度选择

✅ **个性化推荐**
- 根据用户兴趣标签进行智能推荐
- 学习用户偏好，持续优化
- 支持多个兴趣领域

✅ **灵活配置**
- 自定义兴趣标签
- 可选的自动下载功能
- 支持多种语言

✅ **跨浏览器支持**
- Chrome/Chromium
- Firefox
- Edge
- Brave
- 其他 Chromium 内核浏览器

### 用户界面

- 现代化弹出窗口，直观易用
- 完整的设置页面
- 实时进度显示
- 错误提示和提醒

## 安装指南

### Chrome

#### 方式一：从 ZIP 文件安装

1. 下载最新的 `video-ai-chrome-*.zip`
2. 解压到任意文件夹
3. 打开 Chrome，进入 `chrome://extensions/`
4. 启用右上角的 **开发者模式**
5. 点击 **加载未封装的扩展程序**
6. 选择解压的扩展文件夹

#### 方式二：开发者模式直接加载

```bash
# 1. 克隆或下载项目
cd /path/to/video-ai/browser-extension

# 2. 打开 Chrome 的扩展管理页面
# chrome://extensions/

# 3. 启用开发者模式
# 点击右上角的开关

# 4. 点击"加载未封装的扩展程序"
# 选择当前目录
```

### Firefox

1. 下载最新的 `video-ai-firefox-*.zip`
2. 解压到任意文件夹
3. 打开 Firefox，进入 `about:debugging#/runtime/this-firefox`
4. 点击 **加载临时附加组件**
5. 选择解压文件夹中的 `manifest.json`

**注意**：Firefox 中临时加载的扩展在浏览器重启后会移除。要永久安装，请通过 Firefox Add-ons 官方商店安装。

### Edge

1. 下载最新的 `video-ai-edge-*.zip`
2. 解压到任意文件夹
3. 打开 Edge，进入 `edge://extensions/`
4. 启用左下角的 **开发者模式**
5. 点击 **加载未封装的扩展程序**
6. 选择解压的扩展文件夹

## 快速开始

### 1. 获取 API Token

访问 [Video-AI 控制面板](https://console.video-ai.com) 获取您的 API Token：

1. 登录您的账户
2. 进入 **API 密钥** 页面
3. 点击 **生成新密钥**
4. 复制 Token 值

### 2. 配置扩展

1. 打开扩展的 **设置** 页面（点击弹出窗口的 ⚙️ 按钮）
2. 进入 **账户设置** 标签页
3. 粘贴 API Token
4. 点击 **测试连接** 验证 Token 有效性
5. 根据需要配置其他设置

### 3. 开始使用

1. 打开任何 YouTube 视频
2. 点击 YouTube 播放器控制栏右边的 🎯 按钮
3. 在弹出窗口中配置剪辑参数
4. 点击 **智能剪辑** 开始处理
5. 等待处理完成，下载编辑后的视频

## 使用指南

### 弹出窗口

#### 当前视频信息

显示当前 YouTube 页面的视频信息：
- 视频标题
- 视频 ID
- 视频 URL

#### 处理设置

**兴趣标签**
- 输入您感兴趣的话题（用逗号分隔）
- 示例：`AI, 编程, 机器学习, Python`
- 这些标签将用于识别您最感兴趣的内容片段

**输出长度**
- **短**：编辑后视频为原视频长度的 30%
- **中**：编辑后视频为原视频长度的 50%（推荐）
- **长**：编辑后视频为原视频长度的 70%

#### 智能剪辑按钮

点击 **🎯 智能剪辑** 开始处理：
- 视频会发送到 Video-AI 服务处理
- 显示实时进度
- 处理完成后提供下载链接

#### 更多设置按钮

点击 **⚙️ 更多设置** 打开完整设置页面

### 设置页面

#### 账户设置

**API Token**
- 粘贴您的 API Token
- 点击 **测试连接** 验证有效性
- 连接成功后自动保存用户 ID

**用户 ID**
- 从您的账户自动获取
- 只读字段

#### 偏好设置

**兴趣标签**
- 多行文本框，每行一个或逗号分隔
- 支持中文和英文
- 直接影响视频编辑结果

**默认输出长度**
- 设置默认的剪辑长度

**语言**
- 选择扩展的界面语言
- 支持中文和英文

#### 高级选项

**自动下载**
- 启用后，处理完成的视频会自动下载
- 下载到您的默认下载文件夹

**桌面通知**
- 启用后，处理完成时显示系统通知

**保存处理历史**
- 启用后，记录所有处理过的视频
- 可在历史记录页面查看

**缓存过期时间**
- 设置本地缓存的保留天数
- 超过此时间的缓存自动清除

**设置导入/导出**
- **导出设置**：将当前设置保存为 JSON 文件
- **导入设置**：从 JSON 文件恢复设置
- 便于在多个设备间同步配置

## 配置选项

### 存储位置

所有设置都存储在浏览器的同步存储中（`chrome.storage.sync`）：

```javascript
{
  apiToken: string,           // API 认证 Token
  userId: string,             // 用户 ID
  interests: string,          // 兴趣标签（逗号分隔）
  outputLength: string,       // 输出长度 (short|medium|long)
  language: string,           // 界面语言 (zh-CN|zh-TW|en)
  autoDownload: boolean,      // 是否自动下载
  enableNotifications: boolean, // 是否启用通知
  saveHistory: boolean,       // 是否保存历史
  cacheDays: number           // 缓存过期天数
}
```

### 环境变量

项目使用 `manifest.json` 中的配置：

```json
{
  "manifest_version": 3,
  "version": "1.0.0",
  "permissions": ["activeTab", "scripting", "storage"],
  "host_permissions": ["https://www.youtube.com/*", "https://youtu.be/*"]
}
```

## API 配置

### API 端点

Video-AI 提供以下 API 端点：

#### 认证

**验证 Token**
```
POST https://api.video-ai.com/api/v1/auth/verify
Authorization: Bearer {token}
```

响应：
```json
{
  "status": "success",
  "user_id": "user_123",
  "user_name": "John Doe",
  "api_version": "1.0.0"
}
```

#### 视频处理

**启动处理**
```
POST https://api.video-ai.com/api/v1/videos/process
Authorization: Bearer {token}
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=...",
  "user_interests": ["AI", "编程"],
  "output_length": "medium"
}
```

响应：
```json
{
  "status": "success",
  "job_id": "job_abc123",
  "estimated_duration": 300
}
```

**查询任务状态**
```
GET https://api.video-ai.com/api/v1/jobs/{job_id}
Authorization: Bearer {token}
```

响应：
```json
{
  "status": "processing",
  "progress": 45,
  "current_step": "scene_detection",
  "message": "正在检测场景..."
}
```

或者（完成时）：

```json
{
  "status": "completed",
  "progress": 100,
  "result": {
    "video_url": "https://download.video-ai.com/...",
    "stats": {
      "original_duration": 3600,
      "edited_duration": 1800,
      "retention_rate": 50
    }
  }
}
```

## 开发指南

### 项目结构

```
browser-extension/
├── manifest.json              # 扩展配置（Manifest V3）
├── popup.html                 # 弹出窗口 HTML
├── popup.js                   # 弹出窗口逻辑（140+ 行，含完整 API 调用）
├── content.js                 # 内容脚本（YouTube 页面集成）
├── background.js              # 后台脚本（定时任务和消息处理）
├── options.html               # 设置页面 HTML（230+ 行）
├── options.js                 # 设置逻辑（350+ 行，含导入/导出）
├── styles/
│   ├── popup.css              # 弹出和设置页面样式（400+ 行）
│   ├── options.css            # 设置页面专用样式（300+ 行）
│   └── content.css            # YouTube 页面样式注入
├── icons/
│   ├── icon16.png             # 16x16 图标
│   ├── icon48.png             # 48x48 图标
│   └── icon128.png            # 128x128 图标
├── build.sh                   # 打包脚本
└── README.md                  # 本文档
```

### 开发环境设置

1. **克隆项目**
```bash
cd /home/user/tvbox1/video-ai/browser-extension
```

2. **本地测试（Chrome）**
```bash
# 打开 chrome://extensions/
# 启用"开发者模式"
# 点击"加载未封装的扩展程序"
# 选择当前目录
```

3. **修改代码**
```bash
# 编辑 JavaScript 或 CSS 文件
# 修改后点击扩展下方的"刷新"按钮即可看到变化
```

### 构建和打包

```bash
# 打包所有浏览器版本
./build.sh

# 输出文件将位于 dist/ 目录
# - video-ai-chrome-1.0.0.zip
# - video-ai-firefox-1.0.0.zip
# - video-ai-edge-1.0.0.zip
# - checksums.txt
```

### 代码风格

- 使用 ES6+ 特性
- 注释使用 JSDoc 格式
- 样式使用 CSS 变量
- 遵循 Google JavaScript Style Guide

### 关键实现

#### popup.js - API 集成

```javascript
// 带超时的 fetch
function fetchWithTimeout(url, options, timeout) {
  return Promise.race([
    fetch(url, options),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('超时')), timeout)
    )
  ]);
}

// 轮询任务状态
async function pollJobStatus(jobId, apiToken) {
  // 每 2 秒查询一次
  // 最多轮询 180 次（6 小时）
}
```

#### content.js - YouTube 集成

```javascript
// 在 YouTube 播放器控制栏中注入按钮
function addVideoAIButton() {
  const controls = document.querySelector('.ytp-right-controls');
  // 创建 🎯 按钮
}

// 监听 YouTube SPA 导航
const observer = new MutationObserver(() => {
  // 检查 URL 变化
  // 重新添加按钮（需要时）
});
```

#### background.js - 后台任务

```javascript
// 定时同步设置
chrome.alarms.create('syncSettings', { periodInMinutes: 60 });

// 检查待处理任务
chrome.alarms.create('checkJobs', { periodInMinutes: 5 });
```

## 常见问题

### Q1：如何获取 API Token？

访问 [Video-AI 控制面板](https://console.video-ai.com)，登录后进入 API 密钥管理页面。

### Q2：为什么视频处理失败？

常见原因：
- API Token 无效或已过期 → 重新获取 Token
- 网络连接不稳定 → 检查网络设置
- 视频无法访问 → 确保您有权访问该视频
- API 服务故障 → 稍后重试或联系支持

### Q3：支持哪些视频格式？

当前支持所有 YouTube 视频。将来可能支持：
- Bilibili
- Vimeo
- 本地视频文件

### Q4：处理需要多长时间？

处理时间取决于：
- 视频长度（通常为视频长度的 5-20%）
- 当前服务器负载
- 输出长度设置

通常 1-3 小时的视频处理 5-15 分钟。

### Q5：我的数据会被保存吗？

- 只有处理结果 URL 保存在您的账户中
- 视频数据在处理完成后 7 天内自动删除
- 您的偏好设置仅保存在浏览器本地（同步存储）

### Q6：如何卸载扩展？

**Chrome/Edge**：
1. 打开 `chrome://extensions/` 或 `edge://extensions/`
2. 找到 Video-AI
3. 点击右下角的 **移除**

**Firefox**：
1. 打开 `about:addons`
2. 找到 Video-AI
3. 点击 **移除**

### Q7：支持离线使用吗？

不支持。扩展需要网络连接才能：
- 验证 API Token
- 向服务器发送视频 URL
- 查询处理状态
- 下载编辑后的视频

### Q8：我可以修改或再分发这个扩展吗？

可以！本项目采用 MIT 许可证，您可以：
- 修改源代码
- 为个人或企业使用编译
- 发布修改后的版本（需声明修改内容）

详见 [许可证](#许可证) 部分。

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. **Fork 项目**
2. **创建功能分支** (`git checkout -b feature/amazing-feature`)
3. **提交更改** (`git commit -m 'Add amazing feature'`)
4. **推送到分支** (`git push origin feature/amazing-feature`)
5. **开启 Pull Request**

### 发现 Bug？

请在 [Issues](https://github.com/your-repo/issues) 页面提交详细的 bug 报告。

### 建议新功能？

欢迎在 [Discussions](https://github.com/your-repo/discussions) 中分享您的想法。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

```
MIT License

Copyright (c) 2024 Video-AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 支持

- 📖 [官方文档](https://docs.video-ai.com)
- 🐛 [报告 Bug](https://github.com/your-repo/issues)
- 💬 [讨论社区](https://github.com/your-repo/discussions)
- 📧 [联系我们](mailto:support@video-ai.com)

## 相关资源

- [Video-AI 官网](https://video-ai.com)
- [Video-AI API 文档](https://api.video-ai.com/docs)
- [Chrome 扩展开发指南](https://developer.chrome.com/docs/extensions/)
- [Firefox WebExtensions 指南](https://developer.mozilla.org/docs/Mozilla/Add-ons/WebExtensions)
- [Manifest V3 文档](https://developer.chrome.com/docs/extensions/mv3/)

---

**最后更新**：2024 年 11 月
**维护者**：Video-AI Team
