# Video-AI 浏览器扩展 - 快速安装指南

## 快速安装（3 分钟）

### 步骤 1：选择您的浏览器

#### Chrome / Chromium / Brave / Edge

1. **打开扩展管理页面**
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`
   - Brave: `brave://extensions/`

2. **启用开发者模式**
   - 点击右上角的 **开发者模式** 开关

3. **加载扩展**
   - 点击 **加载未封装的扩展程序**
   - 选择 `/home/user/tvbox1/video-ai/browser-extension` 目录

4. **验证安装**
   - 扩展列表中应该看到 "Video-AI - 智能视频编辑"
   - 扩展图标应该出现在地址栏右边

#### Firefox

1. **打开调试页面**
   - 输入 `about:debugging#/runtime/this-firefox` 到地址栏
   - 或进入 Menu → Add-ons → Extensions → 齿轮图标 → Debug Add-ons

2. **加载临时扩展**
   - 点击 **Load Temporary Add-on**
   - 选择 `/home/user/tvbox1/video-ai/browser-extension/manifest.json`

3. **验证安装**
   - Add-ons 页面应该显示 "Video-AI - 智能视频编辑"
   - 临时加载的扩展在重启浏览器后会移除

### 步骤 2：配置 API Token

1. **打开设置页面**
   - 点击浏览器工具栏中的 Video-AI 图标
   - 在弹出窗口中点击 **⚙️ 更多设置**

2. **输入 API Token**
   - 获取地址：https://console.video-ai.com
   - 进入 **API 密钥** 管理页面
   - 复制您的 Token

3. **验证连接**
   - 粘贴 Token 到 **API Token** 字段
   - 点击 **🔗 测试连接** 按钮
   - 看到 "✅ 连接成功" 提示

4. **保存设置**
   - 点击 **✅ 保存设置** 按钮

### 步骤 3：开始使用

1. **访问 YouTube**
   - 打开任意 YouTube 视频

2. **启动智能剪辑**
   - 在播放器控制栏右边找到 **🎯** 按钮
   - 点击打开弹出窗口

3. **配置参数**
   - **兴趣标签**：输入您的兴趣（如：AI, 编程, 机器学习）
   - **输出长度**：选择视频长度（推荐选择"中"）

4. **开始处理**
   - 点击 **🎯 智能剪辑** 按钮
   - 等待处理完成（通常 5-15 分钟）
   - 点击 **📥 下载视频** 保存编辑后的视频

## 常见问题

### 我没有看到 🎯 按钮

**可能原因**：
1. 您没有在 YouTube 视频页面
2. 扩展未正确加载
3. YouTube 页面需要刷新

**解决方案**：
- 刷新 YouTube 页面 (F5)
- 检查 Chrome 扩展管理页面确认扩展已启用
- 重新加载扩展（点击下方的 **刷新** 按钮）

### "API Token 无效" 错误

**可能原因**：
1. Token 已过期
2. Token 输入错误
3. Token 所有者的账户有问题

**解决方案**：
- 访问 https://console.video-ai.com 重新生成 Token
- 检查 Token 是否有多余空格
- 确保您的账户处于活跃状态

### 视频处理失败

**可能原因**：
1. 网络连接不稳定
2. YouTube 服务出现问题
3. 视频无法下载
4. API 服务故障

**解决方案**：
- 检查您的网络连接
- 尝试其他 YouTube 视频
- 稍后重试或联系支持

### 如何卸载扩展？

**Chrome/Edge**：
1. 打开 `chrome://extensions/` 或 `edge://extensions/`
2. 找到 "Video-AI - 智能视频编辑"
3. 点击 **移除** 或垃圾箱图标

**Firefox**：
1. 打开 `about:addons`
2. 找到 "Video-AI - 智能视频编辑"
3. 点击 **移除** 或垃圾箱图标

## 高级配置

### 自动下载设置

1. 打开扩展设置 (⚙️ 更多设置)
2. 进入 **高级选项** 标签页
3. 勾选 **启用自动下载**
4. 保存设置

现在视频处理完成后会自动下载到您的下载文件夹。

### 启用桌面通知

1. 打开扩展设置
2. 进入 **高级选项**
3. 勾选 **启用桌面通知**
4. 保存设置

您会在视频处理完成时收到系统通知。

### 导出和导入设置

**导出**：
1. 打开设置页面
2. 进入 **高级选项**
3. 点击 **💾 导出设置**
4. 保存 JSON 文件到安全位置

**导入**：
1. 打开设置页面
2. 进入 **高级选项**
3. 点击 **📂 导入设置**
4. 选择之前导出的 JSON 文件

## 获取帮助

- **官方文档**：https://docs.video-ai.com
- **GitHub Issues**：https://github.com/your-repo/issues
- **社区讨论**：https://github.com/your-repo/discussions
- **联系支持**：support@video-ai.com

## 反馈和建议

如果您发现 bug 或有功能建议，欢迎：

1. 在 GitHub Issues 中报告
2. 在 GitHub Discussions 中讨论
3. 发送邮件到 support@video-ai.com

## 隐私政策

- 我们不收集您的个人信息
- 不追踪您的浏览历史
- 视频处理完成后自动删除
- 所有设置仅保存在您的浏览器本地

---

**需要帮助？** 查看 [README.md](README.md) 获取完整文档。
