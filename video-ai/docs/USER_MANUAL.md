# Video-AI 用户手册

欢迎使用 Video-AI 个性化智能视频编辑系统！本手册将帮助您快速上手并充分利用系统的各项功能。

---

## 目录

1. [系统概述](#系统概述)
2. [Web UI 使用指南](#web-ui-使用指南)
3. [API 使用示例](#api-使用示例)
4. [浏览器插件使用](#浏览器插件使用)
5. [常见问题解答](#常见问题解答)
6. [故障排除](#故障排除)

---

## 系统概述

### Video-AI 是什么？

Video-AI 是一个AI驱动的视频编辑系统，能够：
- 🎯 根据您的兴趣自动提取视频中相关内容
- ⏱️ 将视频压缩至原时长的30-70%
- 📊 提升信息密度2-3倍
- 🎬 使用AI生成自然的过渡效果

### 核心功能

#### 阶段一：智能片段提取
- 视频转录与语音识别
- 基于兴趣的内容筛选
- 自动剪辑和拼接
- 专业过渡效果

#### 阶段二：智能叙事生成
- 叙事逻辑优化
- 视频质量分析
- 场景智能检测
- AI视频过渡

#### 阶段三：深度个性化
- 用户画像系统
- 实时推荐引擎
- 反馈学习
- 协同过滤推荐

---

## Web UI 使用指南

### 启动 Web UI

```bash
# 方式1：使用启动脚本
./run_web_ui.sh

# 方式2：直接运行
streamlit run examples/web_ui.py
```

然后在浏览器中访问: **http://localhost:8501**

### 界面概览

Web UI 包含4个主要标签页：

1. **视频处理** - 处理本地或YouTube视频
2. **用户画像** - 管理个人兴趣和偏好
3. **处理历史** - 查看历史记录和推荐
4. **文件管理** - 管理输入输出文件

---

### 1. 视频处理

#### 步骤1：选择视频输入方式

**方式A：本地文件上传**
1. 点击 "上传本地视频" 下拉框
2. 点击 "Browse files" 按钮
3. 选择视频文件（支持 MP4, AVI, MOV 等格式）
4. 等待上传完成

**方式B：YouTube 链接**
1. 点击 "YouTube 链接" 下拉框
2. 在输入框中粘贴 YouTube 视频URL
   - 例如：`https://www.youtube.com/watch?v=dQw4w9WgXcQ`
3. 点击 "下载" 按钮
4. 等待下载完成（进度条显示）

**方式C：选择已有文件**
1. 点击 "选择已有文件" 下拉框
2. 从下拉列表中选择之前上传的文件

#### 步骤2：配置处理选项

**基础配置**：

**用户ID**
- 输入您的用户ID（用于保存个人偏好）
- 例如：`user_001`

**用户兴趣**
- 输入您的兴趣标签，用逗号分隔
- 例如：`人工智能, 机器学习, 深度学习, 计算机视觉`
- 系统会优先保留与这些主题相关的内容

**跳过主题**（可选）
- 输入您不感兴趣的主题
- 例如：`广告, 闲聊, 废话`
- 这些内容会被自动过滤

**输出长度**
- **Short (30%)**：只保留最相关的内容
- **Medium (50%)**：平衡模式
- **Long (70%)**：保留大部分内容

**节奏**
- **Slow**：慢节奏，更多过渡
- **Normal**：标准节奏
- **Fast**：快节奏，简洁明了

**高级配置**（展开查看）：

**分析模式**
- **LLM模式**：使用GPT-4/Gemini等大模型分析（更精准，需要API密钥）
- **NLP模式**：使用传统NLP技术（免费，速度快）

**LLM提供商**（仅LLM模式）
- **OpenAI (GPT-4)**：最精准，成本中等
- **Google (Gemini)**：有免费额度
- **Anthropic (Claude)**：性价比高

**过渡风格**
- **text**：文字卡片过渡
- **fade**：淡入淡出
- **blur**：模糊过渡
- **zoom**：缩放过渡
- **ai_generated**：AI生成的创意过渡（需要GPU）

**质量阈值** (1-10)
- 设置视频质量最低分数
- 低于此分数的片段会被自动过滤

#### 步骤3：开始处理

1. 检查所有配置是否正确
2. 点击 "🚀 开始处理" 按钮
3. 观察处理进度：
   - 📝 正在转录视频... (30%)
   - 🧠 正在分析内容... (60%)
   - ✂️ 正在剪辑视频... (90%)
   - ✅ 处理完成！(100%)

#### 步骤4：查看结果

处理完成后，您将看到：

**处理摘要**
```
✅ 视频处理完成！

原始时长: 600.0 秒
编辑后时长: 180.0 秒
压缩率: 70.0%
包含片段数: 5
输出文件: data/output/user_001_edited_20241117_123456.mp4
```

**下载按钮**
- 点击 "📥 下载编辑后的视频" 按钮下载结果

**详细信息**（展开查看）
- 转录文本
- 分析报告
- 片段详情

---

### 2. 用户画像

管理您的个人偏好和兴趣标签。

#### 查看用户画像

1. 切换到 "用户画像" 标签页
2. 输入您的用户ID
3. 点击 "加载用户画像" 按钮

显示信息：
- 用户ID
- 当前兴趣标签
- 观看历史
- 创建时间
- 最后更新时间

#### 更新兴趣标签

1. 在 "新增兴趣" 输入框中输入标签
2. 点击 "添加兴趣" 按钮
3. 或者在 "移除兴趣" 下拉框中选择要删除的标签
4. 点击 "移除兴趣" 按钮

#### 创建新用户

1. 输入新的用户ID
2. 在 "初始兴趣" 输入框中输入兴趣标签
3. 点击 "创建用户画像" 按钮

---

### 3. 处理历史

查看历史记录并获取个性化推荐。

#### 查看历史记录

1. 切换到 "处理历史" 标签页
2. 查看最近处理的视频列表

显示信息：
- 视频文件名
- 处理时间
- 原始时长
- 编辑后时长
- 压缩率
- 下载链接

#### 个性化推荐

基于您的观看历史和兴趣，系统会推荐相关视频。

**查看推荐**：
1. 选择推荐数量（3/5/10/15）
2. 点击 "🔄 刷新推荐" 按钮
3. 查看推荐列表：
   - 视频ID
   - 相关度分数
   - 推荐原因
   - 点赞按钮（记录您的偏好）

**用户洞察**：
查看您的兴趣分析和行为统计：
- 主要兴趣（Top 5）
- 行为次数
- 平均观看时长

**系统统计**：
查看推荐系统的运行状态：
- 总用户数
- 总视频数
- 热门视频

---

### 4. 文件管理

管理输入和输出文件。

#### 输入文件

- 查看所有上传的输入文件
- 显示文件大小
- 删除不需要的文件

#### 输出文件

- 查看所有生成的输出文件
- 下载视频
- 删除旧文件释放空间

#### 批量操作

- 清空输入文件夹
- 清空输出文件夹
- **警告**：此操作不可恢复！

---

## API 使用示例

如果您是开发者，可以通过Python API直接调用Video-AI的功能。

### 基础用法

```python
from src.core.editor import VideoEditor

# 创建编辑器
editor = VideoEditor(
    user_interests=["AI", "机器学习"],
    output_length="medium"
)

# 处理视频
result = editor.edit_video(
    input_path="input.mp4",
    output_path="output.mp4"
)

# 打印结果
print(f"压缩率: {result['compression_ratio']:.1%}")
print(f"处理时长: {result['edited_duration']}秒")
```

### YouTube视频处理

```python
from src.utils.youtube_downloader import YouTubeDownloader
from src.core.editor import VideoEditor

# 下载YouTube视频
downloader = YouTubeDownloader(output_dir="data/youtube")
download_result = downloader.download_video(
    "https://www.youtube.com/watch?v=VIDEO_ID"
)

# 处理视频
editor = VideoEditor(user_interests=["科技"])
result = editor.edit_video(
    download_result['video_path'],
    "output.mp4"
)
```

### 个性化推荐

```python
from src.services.personalization import PersonalizationService

# 创建服务
service = PersonalizationService(enable_realtime=True)

# 创建用户
service.create_user_profile(
    user_id="user_001",
    initial_interests=["AI", "编程"]
)

# 追踪行为
service.track_user_action(
    user_id="user_001",
    action="view",
    video_id="video_001",
    duration=600
)

# 获取推荐
recommendations = service.get_realtime_recommendations(
    user_id="user_001",
    num=5
)
```

详细API文档请参考: [API_REFERENCE.md](API_REFERENCE.md)

---

## 浏览器插件使用

**注意**: 浏览器插件功能正在开发中，预计2025 Q1发布。

### 功能预览

- 🌐 在YouTube页面直接调用Video-AI
- ⚡ 一键处理当前观看的视频
- 📊 实时显示视频信息密度
- 🔖 保存个人兴趣设置
- 📥 快速下载编辑后的视频

### 安装步骤（即将推出）

1. 访问Chrome Web Store / Firefox Add-ons
2. 搜索 "Video-AI"
3. 点击 "添加到浏览器"
4. 配置API端点和个人设置
5. 访问YouTube即可使用

---

## 常见问题解答

### Q1: 为什么处理速度慢？

**A**: 处理速度取决于多个因素：

1. **硬件配置**
   - CPU模式较慢，建议使用GPU
   - 内存不足会导致速度下降

2. **分析模式**
   - LLM模式需要调用API，速度较慢
   - 建议使用NLP模式（免费且快速）

3. **视频质量**
   - 高分辨率视频处理时间更长
   - 可以在设置中降低输出质量

**优化建议**：
- 使用GPU加速
- 切换到NLP模式
- 降低视频分辨率
- 关闭AI过渡生成

### Q2: 为什么需要API密钥？

**A**: API密钥是可选的！

- **不提供API密钥**：系统使用免费的NLP模式，功能完整
- **提供API密钥**：可以使用LLM模式，分析更精准

### Q3: 支持哪些视频格式？

**A**: 支持所有FFmpeg支持的格式：
- MP4, AVI, MOV, MKV, WebM
- FLV, WMV, MPEG, 3GP
- 等等

### Q4: 可以批量处理视频吗？

**A**: 可以！使用Python API：

```python
from src.core.editor import VideoEditor
import os

editor = VideoEditor(user_interests=["AI"])

for video_file in os.listdir("input_folder"):
    if video_file.endswith(".mp4"):
        editor.edit_video(
            f"input_folder/{video_file}",
            f"output_folder/{video_file}"
        )
```

### Q5: 处理后的视频质量如何？

**A**:
- 视频质量取决于原始视频和设置
- 默认情况下，输出质量与输入相同
- 可以通过 `quality_threshold` 参数控制质量

### Q6: 会丢失重要内容吗？

**A**:
- 系统只过滤与您兴趣不相关的内容
- 重要内容会根据相关性评分保留
- 您可以调整 `output_length` 控制保留比例

### Q7: 如何提高准确率？

**A**:
1. **精确的兴趣标签**：提供详细的兴趣描述
2. **使用LLM模式**：更智能的内容理解
3. **调整输出长度**：增加保留比例
4. **使用反馈**：点赞/点踩帮助系统学习

### Q8: 支持多语言吗？

**A**:
- 转录：支持Whisper支持的所有语言
- 分析：目前支持中文和英文
- UI：目前仅中文，英文版开发中

### Q9: 数据会被上传吗？

**A**:
- 本地模式（NLP）：所有处理在本地完成，数据不上传
- LLM模式：只有文本（转录结果）发送给API，视频不上传
- 您的隐私完全受保护

### Q10: 可以商用吗？

**A**:
- 项目采用MIT许可证，允许商用
- 但请注意API使用条款（如果使用LLM模式）
- 建议自建服务器部署

---

## 故障排除

### 问题1: Web UI无法启动

**症状**：运行 `streamlit run examples/web_ui.py` 后浏览器无法打开

**解决方案**：
```bash
# 检查端口是否被占用
lsof -i:8501

# 指定其他端口
streamlit run examples/web_ui.py --server.port 8502

# 检查依赖
pip install streamlit --upgrade
```

### 问题2: 转录失败

**症状**：处理时在转录阶段卡住或报错

**解决方案**：
```bash
# 检查FFmpeg是否安装
ffmpeg -version

# 重新安装whisper
pip install openai-whisper --upgrade

# 尝试使用CPU模式
# 在代码中设置：device="cpu"
```

### 问题3: LLM API调用失败

**症状**：显示 "API Error" 或 "Rate Limit"

**解决方案**：
1. **检查API密钥**：确保密钥正确且有效
2. **检查余额**：确保账户有足够额度
3. **降级到NLP**：系统会自动降级，也可手动设置
4. **重试机制**：系统会自动重试，请等待

### 问题4: 输出视频播放不了

**症状**：生成的视频无法播放

**解决方案**：
```bash
# 检查输出文件是否完整
ls -lh data/output/

# 尝试用VLC播放器打开
vlc output.mp4

# 重新编码视频
ffmpeg -i output.mp4 -c:v libx264 -c:a aac output_fixed.mp4
```

### 问题5: 内存不足

**症状**：处理大视频时系统卡死或崩溃

**解决方案**：
1. **降低分辨率**：
   ```python
   editor = VideoEditor(
       ...,
       max_resolution=(1280, 720)  # 限制最大分辨率
   )
   ```

2. **分段处理**：将长视频分成多段处理

3. **关闭其他程序**：释放内存

4. **增加虚拟内存**（Linux）：
   ```bash
   sudo dd if=/dev/zero of=/swapfile bs=1G count=8
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### 问题6: GPU不被识别

**症状**：虽然有GPU但是使用CPU处理

**解决方案**：
```bash
# 检查CUDA版本
nvidia-smi

# 重新安装PyTorch（CUDA版本）
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 测试GPU
python -c "import torch; print(torch.cuda.is_available())"
```

### 问题7: YouTube下载失败

**症状**：无法下载YouTube视频

**解决方案**：
```bash
# 更新yt-dlp
pip install yt-dlp --upgrade

# 检查是否被地区限制
# 使用代理：
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# 尝试其他格式
# 在代码中设置：format='best[height<=720]'
```

---

## 获取帮助

如果本手册没有解决您的问题，请通过以下方式获取帮助：

### 1. 查看其他文档

- [开发者指南](DEVELOPER_GUIDE.md) - 技术细节和架构
- [API参考](API_REFERENCE.md) - 完整API文档
- [部署指南](DEPLOYMENT_GUIDE.md) - 服务器部署

### 2. 搜索已有问题

访问 GitHub Issues: https://github.com/yourusername/video-ai/issues

### 3. 提交新问题

如果您的问题是新的，请[创建Issue](https://github.com/yourusername/video-ai/issues/new)，并提供：
- 问题描述
- 错误信息（如果有）
- 系统信息（OS, Python版本, GPU等）
- 复现步骤

### 4. 加入社区

- Discord: https://discord.gg/video-ai
- 微信群：扫描二维码加入

---

## 更新日志

### v1.0.0 (2024-11)

- ✅ 完成阶段一、二、三所有功能
- ✅ Web UI 上线
- ✅ YouTube集成
- ✅ 实时推荐系统
- ✅ 反馈学习系统

### 即将推出

- 🔄 浏览器插件 (2025 Q1)
- 📱 移动端应用 (2025 Q2)
- 🌐 RESTful API (2025 Q1)
- 🧪 A/B测试框架 (2025 Q1)

---

<div align="center">

**感谢使用 Video-AI！**

如果觉得有帮助，请给我们一个 ⭐ Star！

[GitHub](https://github.com/yourusername/video-ai) |
[文档](https://video-ai.readthedocs.io) |
[问题反馈](https://github.com/yourusername/video-ai/issues)

</div>
