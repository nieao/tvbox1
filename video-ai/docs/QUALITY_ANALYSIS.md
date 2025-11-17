# 视频质量分析系统

## 概述

Video-AI 的质量分析系统提供了全面的视频质量评估功能，包括视觉质量、音频质量、技术规格等多个维度。系统能够自动识别视频的问题并提供改进建议。

## 功能特性

### 1. 视觉质量分析

系统分析以下视觉指标：

| 指标 | 说明 | 评分范围 | 优化建议 |
|------|------|--------|--------|
| **清晰度** | 基于Laplacian方差计算，反映图像锐度 | 0-100 | < 40时应用锐化滤镜 |
| **亮度** | 相对于理想亮度(127/255)的偏差 | 0-100 | < 40增加亮度；> 85降低亮度 |
| **对比度** | 基于像素标准差 | 0-100 | < 40时应增加对比度 |
| **色彩平衡** | RGB通道的均衡度 | 0-100 | < 50时进行色彩校正 |

### 2. 音频质量分析

系统分析以下音频指标：

| 指标 | 说明 | 单位 | 优化建议 |
|------|------|-----|--------|
| **音量** | 音频的响度水平 | dB | -15~-3dB为最优范围 |
| **噪音水平** | 背景噪音的多少 | 0-100 | > 60时需要降噪处理 |
| **清晰度** | 基于峰值因子 | 0-100 | < 50时需要改进音频质量 |

### 3. 技术质量检测

系统检测以下技术参数：

| 参数 | 说明 | 推荐值 | 最低要求 |
|------|------|-------|--------|
| **分辨率** | 视频的像素尺寸 | 1920x1080+ | 1280x720+ |
| **帧率** | 每秒帧数 | 30fps或60fps | 24fps+ |
| **码率** | 数据传输速率 | 5000+kbps | 2000+kbps |

### 4. 综合质量评分

系统计算综合评分（0-100），权重分配如下：

```
综合评分 = 视觉质量 × 40% + 音频质量 × 30% + 技术质量 × 30%

视觉质量权重分配：
  - 清晰度: 35%
  - 亮度: 20%
  - 对比度: 25%
  - 色彩平衡: 20%

音频质量权重分配：
  - 音量: 40%
  - 噪音: 30%
  - 清晰度: 30%

技术质量权重分配：
  - 分辨率: 40%
  - 帧率: 35%
  - 码率: 25%
```

评分等级：
- **80-100**: 优秀 ✅ - 无需特殊处理
- **70-79**: 良好 ⭐ - 可选择性改进
- **60-69**: 一般 ⚠️ - 建议应用改进处理
- **0-59**: 较差 ❌ - 强烈建议改进或使用其他源

## API 使用指南

### 基本使用

```python
from src.core.quality_analyzer import QualityAnalyzer

# 创建分析器
analyzer = QualityAnalyzer()

# 分析视频
metrics = analyzer.analyze_video("video.mp4")

# 获取综合评分
print(f"质量评分: {metrics.overall_score}/100")

# 生成报告
report = analyzer.generate_quality_report(metrics)
print(report)
```

### 获取改进建议

```python
# 获取改进建议
suggestions = analyzer.suggest_enhancements(metrics)
for suggestion in suggestions:
    print(suggestion)
```

### 访问详细指标

```python
# 视觉质量
print(f"清晰度: {metrics.sharpness:.1f}/100")
print(f"亮度: {metrics.brightness:.1f}/100")
print(f"对比度: {metrics.contrast:.1f}/100")
print(f"色彩平衡: {metrics.color_balance:.1f}/100")

# 音频质量
print(f"音量: {metrics.audio_loudness:.1f}dB")
print(f"噪音: {metrics.audio_noise:.1f}/100")
print(f"清晰度: {metrics.audio_clarity:.1f}/100")

# 技术参数
print(f"分辨率: {metrics.resolution[0]}x{metrics.resolution[1]}")
print(f"帧率: {metrics.fps:.1f}fps")
print(f"码率: {metrics.bitrate}kbps")
```

### 导出为JSON

```python
import json

# 转换为字典
metrics_dict = metrics.to_dict()

# 修复分辨率元组
metrics_dict['resolution'] = list(metrics_dict['resolution'])

# 保存为JSON
with open('quality_metrics.json', 'w') as f:
    json.dump(metrics_dict, f, indent=2)
```

## 在视频编辑中的应用

质量分析器已集成到 VideoEditor 中，在处理视频时会自动进行质量检测：

```python
from src.core.editor import VideoEditor

editor = VideoEditor(user_interests=["编程", "AI"])

# 处理视频时会自动分析质量
result = editor.process_video("input.mp4", "output.mp4")

# 输出样例：
# 分析视频质量...
# 视频综合质量评分: 78.5/100
# 分辨率: 1920x1080 | 帧率: 30.0fps | 码率: 8500kbps
# 质量改进建议:
#   建议：应用锐化滤镜提升清晰度（当前: 65.0/100）
```

## 演示和示例

### 运行质量分析演示

```bash
# 单个视频分析
python examples/quality_demo.py --mode single

# 批量视频分析
python examples/quality_demo.py --mode batch

# 视频对比分析
python examples/quality_demo.py --mode compare

# 视频质量优化建议
python examples/quality_demo.py --mode tips
```

### 演示脚本说明

#### 单个视频分析 (`--mode single`)
- 分析单个视频的完整质量指标
- 生成详细的质量分析报告
- 保存结果为JSON格式

#### 批量视频分析 (`--mode batch`)
- 分析目录下所有视频
- 汇总统计平均评分、最高/最低评分
- 保存批量结果为JSON

#### 视频对比分析 (`--mode compare`)
- 对比两个视频的质量差异
- 逐项比较各个指标
- 判断质量优劣

#### 优化建议 (`--mode tips`)
- 显示视频录制和优化的最佳实践
- 涵盖清晰度、亮度、音频、技术参数等方面

## 质量优化建议

### 录制阶段

#### 视觉质量
- **清晰度**: 使用高分辨率摄像头，确保适当焦点和对焦
- **亮度**: 在充足光线下录制，避免逆光或强反差
- **对比度**: 使用合适的场景和背景，避免单调
- **色彩**: 使用白平衡调整，确保色彩准确

#### 音频质量
- 使用专业麦克风而非内置麦克风
- 在安静环境中录制
- 避免背景噪音、风声、回声
- 保持适当的麦克风距离（10-20cm）

#### 技术参数
- 至少使用1080p (1920×1080) 分辨率
- 帧率不低于24fps（推荐30fps或60fps）
- 码率至少5000kbps（高质量推荐10000+kbps）

### 后期处理阶段

当自动检测到质量问题时，可应用以下处理：

| 问题 | 处理方法 | 工具建议 |
|------|--------|--------|
| 清晰度低 | 应用锐化滤镜 | FFmpeg, OpenCV |
| 亮度过低 | 提升亮度和对比度 | FFmpeg, Adobe Premier |
| 音量过低 | 音频增益 | FFmpeg, Audacity |
| 背景噪音 | 降噪处理 | Audacity, iZotope |
| 色彩偏差 | 色彩分级 | DaVinci Resolve |

## 质量评分参考

### 1080p 视频标准

```
优秀 (80-100):
  - 清晰度: > 75
  - 亮度: 50-90
  - 对比度: 60+
  - 色彩平衡: 60+
  - 音量: -12 ~ -3 dB
  - 码率: 5000+ kbps
  - 帧率: 30+ fps

良好 (70-79):
  - 清晰度: 55-75
  - 亮度: 40-95
  - 对比度: 45-75
  - 色彩平衡: 45-75
  - 音量: -18 ~ 0 dB
  - 码率: 3000+ kbps
  - 帧率: 24+ fps

一般 (60-69):
  - 清晰度: 40-55
  - 亮度: 30-100
  - 对比度: 30-60
  - 色彩平衡: 30-60
  - 音量: -25 ~ +2 dB
  - 码率: 2000+ kbps
  - 帧率: 20+ fps
```

## 常见问题

### Q: 如何快速检查视频质量而不实际处理视频？
A: 直接使用 QualityAnalyzer：
```python
analyzer = QualityAnalyzer()
metrics = analyzer.analyze_video("video.mp4")
print(f"质量评分: {metrics.overall_score:.1f}/100")
```

### Q: 分析需要多长时间？
A: 取决于视频长度和计算机性能。默认采样10帧，通常需要几秒到十几秒。

### Q: 可以跳过音频分析吗？
A: 目前音频分析是可选的。如果pydub未安装，会使用默认值。

### Q: 分析器支持哪些视频格式？
A: 支持所有OpenCV和FFmpeg支持的格式（mp4, avi, mov, mkv, webm等）。

### Q: 如何自定义评分权重？
A: 修改 `_calculate_overall_score()` 方法中的权重参数。

## 技术细节

### 清晰度计算
使用Laplacian算子计算图像梯度的方差：
- 高方差 (>500): 清晰
- 中等方差 (100-500): 一般
- 低方差 (<100): 模糊

### 亮度计算
基于与理想亮度(127/255)的偏差：
- 40-215: 优好范围
- 0-40, 215-255: 过暗或过亮

### 对比度计算
使用灰度图的标准差：
- std < 30: 低对比度
- std 30-80: 中等对比度
- std > 80: 高对比度

### 音频分析
- **音量**: 使用pydub的dBFS测量
- **噪音**: 基于静音段比例
- **清晰度**: 基于峰值因子(峰值/RMS)

## 依赖项

```
opencv-python>=4.5.0
pydub>=0.25.1  (可选，用于音频分析)
```

## 许可证

见项目根目录的 LICENSE 文件。

## 贡献

欢迎提交问题和改进建议！

## 更新日志

### v1.0.0 (2025-11-17)
- 初始发布
- 完整的视觉质量分析
- 完整的音频质量分析
- 技术参数检测
- 综合评分系统
- 自动改进建议
- 详细的质量报告生成
- 集成到VideoEditor
- 演示脚本和文档
