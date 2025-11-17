# Video-AI 移动端应用架构方案

## 1. 技术选型

### 1.1 框架对比分析

| 维度 | React Native | Flutter | 原生开发 |
|------|------------|---------|--------|
| **学习曲线** | 中等（熟悉JS） | 陡峭（Dart） | 陡峭（各平台） |
| **开发速度** | 快速 | 快速 | 较慢 |
| **性能** | 良好 | 优秀 | 最优 |
| **代码复用** | iOS/Android共用 | iOS/Android共用 | 平台特定 |
| **库生态** | 大（npm） | 中等（pub） | 最大 |
| **热更新** | 支持 | 支持 | 不支持 |
| **视频处理** | 第三方库 | 第三方库 | 原生API |
| **开发成本** | 低 | 低 | 高 |
| **应用体积** | 中等 | 小 | 小 |

### 1.2 推荐方案：Flutter + React Native 混合策略

**主要框架：Flutter**
- 优异的性能表现，适合视频处理密集操作
- Dart强类型特性确保代码质量
- 完整的UI框架，Material Design 3支持
- Hot Reload加快开发迭代

**核心原因：**
1. **视频处理性能** - Flutter编译为原生代码，性能接近原生
2. **跨平台统一性** - 代码复用度高（70-80%）
3. **开发效率** - Hot Reload提高开发速度
4. **工具链完整** - DevTools提供完整调试能力
5. **社区支持** - 视频处理库如video_player、ffmpeg_flutter等

**备选方案：React Native**
- 若团队熟悉JavaScript/TypeScript
- 使用react-native-video等成熟库
- 代码共用可扩展到Web端

### 1.3 开发工具链

#### 必需工具
```bash
# Flutter开发环境
- Flutter SDK (3.16+)
- Dart SDK (已包含)
- Android Studio / Xcode
- Android SDK 28+
- iOS 12.0+

# 开发工具
- VS Code with Flutter extension
- Android Emulator / iOS Simulator
- Xcode 13+ (iOS开发)
- Android NDK (视频编码加速)

# CI/CD工具
- GitHub Actions / GitLab CI
- Firebase App Distribution
- TestFlight (iOS)
- Google Play Console
```

#### 推荐IDE配置
```yaml
VS Code Extensions:
  - Flutter (Dart Code)
  - Dart
  - Awesome Flutter Snippets
  - REST Client
  - Thunder Client (API测试)

Android Studio Plugins:
  - Flutter
  - Dart
  - Firebase Tools
```

### 1.4 依赖管理

**核心依赖 (pubspec.yaml)**
```yaml
dependencies:
  flutter:
    sdk: flutter

  # 视频处理
  video_player: ^2.8.1
  ffmpeg_flutter: ^1.0.0
  media_scanner: ^2.0.0

  # 文件处理
  path_provider: ^2.1.1
  file_picker: ^6.1.0

  # 网络请求
  dio: ^5.3.1
  http: ^1.1.0

  # 状态管理
  riverpod: ^2.4.0
  flutter_riverpod: ^2.4.0
  state_notifier: ^1.0.0

  # 本地存储
  hive: ^2.2.3
  shared_preferences: ^2.2.2
  sqflite: ^2.3.0

  # UI组件
  cupertino_icons: ^1.0.6
  flutter_screenutil: ^5.9.0
  getwidget: ^4.3.0

  # 动画
  lottie: ^2.6.0

  # 日志
  logger: ^2.0.1

  # 权限处理
  permission_handler: ^11.4.4

  # 推送通知
  firebase_messaging: ^14.6.0

  # 分析
  firebase_analytics: ^10.7.0
  mixpanel_flutter: ^2.3.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0
  mockito: ^5.4.2
  integration_test:
    sdk: flutter
```

---

## 2. 移动端功能设计

### 2.1 核心功能优先级

#### P0 (MVP必备)
1. **视频导入与预览**
   - 从相机拍摄、相册选择、URL导入
   - 视频预览与裁剪
   - 支持常见格式（MP4, MOV, MKV）

2. **智能剪辑**
   - 一键快速剪辑
   - 显示剪辑进度
   - 结果预览

3. **个性化设置**
   - 兴趣标签选择
   - 输出时长设置（短视频、中等、长视频）
   - 语言选择

4. **结果管理**
   - 编辑历史记录
   - 导出与分享
   - 本地存储管理

#### P1 (功能增强)
5. **高级编辑**
   - 手动片段编辑
   - 过渡效果调整
   - 字幕与配乐

6. **社交分享**
   - TikTok、YouTube、Instagram分享
   - 分享到社交媒体
   - 邀请朋友

#### P2 (未来功能)
7. **推荐系统**
   - 基于用户画像的推荐
   - 内容发现
   - 热门内容排行

8. **用户社区**
   - 用户评分反馈
   - 编辑效果对比
   - 创意分享

### 2.2 移动端特定功能

#### 2.2.1 视频采集功能
```
功能流程：
1. 相机权限申请
   ├─ iOS: AVFoundation
   └─ Android: CameraX

2. 实时预览
   ├─ 帧率：30fps
   ├─ 分辨率：与设备屏幕匹配
   └─ 音频：同步录制

3. 视频保存
   ├─ 格式：MP4 (H.264)
   ├─ 分辨率：自适应
   └─ 位率：自适应（3-25Mbps）
```

#### 2.2.2 离线编辑支持
```
场景1：有限离线编辑
- 本地转录缓存
- 提前下载AI模型（TFLite）
- 支持基础剪辑操作

场景2：完整功能需网络
- 智能剪辑依赖云API
- 过渡生成依赖云计算
- 后台同步编辑结果
```

#### 2.2.3 分享功能
```
支持平台：
├─ 社交媒体：TikTok, Instagram, YouTube Shorts
├─ 通讯工具：WhatsApp, WeChat, Telegram
├─ 云存储：Google Drive, iCloud, OneDrive
└─ 直接分享：AirDrop, Bluetooth

优化策略：
- 自动压缩视频（< 100MB）
- 多个导出格式（竖屏、横屏）
- 后台上传
```

#### 2.2.4 推送通知
```
场景：
1. 编辑完成通知
   - 视频处理完成
   - 生成结果可预览

2. 推荐内容提醒
   - 每日推荐
   - 热门内容发现

3. 社交互动
   - 点赞、评论通知
   - 朋友邀请
```

### 2.3 UI/UX 设计原则

#### 2.3.1 设计系统

**配色方案**
```
Primary Color:
  - Main: #6366F1 (Indigo)
  - Light: #E0E7FF
  - Dark: #312E81

Accent Colors:
  - Success: #10B981
  - Warning: #F59E0B
  - Error: #EF4444

Neutral:
  - Text Primary: #1F2937
  - Text Secondary: #6B7280
  - Background: #F9FAFB
  - Surface: #FFFFFF
```

**排版**
```
Display: 48px - 32px (H1)
Headline: 28px (H2)
Title: 24px (H3)
Body Large: 16px (default)
Body Small: 14px
Label: 12px

Font Family:
  - iOS: San Francisco
  - Android: Roboto
  - Fallback: Inter (custom)
```

**间距**
```
4px - Micro spacing
8px - Minimal spacing
12px - Compact spacing
16px - Default spacing
24px - Comfortable spacing
32px - Large spacing
48px - Extra large spacing
```

#### 2.3.2 关键屏幕设计

**1. 首页 (Home Screen)**
```
布局：
├─ AppBar (固定)
│  ├─ Logo
│  ├─ 用户头像
│  └─ 设置按钮
├─ 主要操作区 (60%)
│  ├─ 大按钮: "+ 导入视频"
│  ├─ 快速预设
│  │  ├─ 短视频模式
│  │  ├─ 学习视频模式
│  │  └─ 会议记录模式
│  └─ 推荐视频（如有）
└─ 底部导航 (40%)
   ├─ 首页 (当前)
   ├─ 历史
   ├─ 下载
   └─ 我的
```

**2. 编辑页面 (Edit Screen)**
```
布局：
├─ 视频预览区 (50%)
│  ├─ 缩略图
│  ├─ 时间轴
│  └─ 播放控制
├─ 参数设置区 (30%)
│  ├─ 兴趣标签选择
│  ├─ 输出时长设置
│  └─ 高级选项
└─ 操作区 (20%)
   ├─ 开始编辑按钮
   └─ 预设加载
```

**3. 处理进度页面 (Processing Screen)**
```
布局：
├─ 进度指示 (30%)
│  ├─ 圆形进度条
│  ├─ 百分比显示
│  └─ 预计时间
├─ 当前状态 (40%)
│  ├─ 转录中...
│  ├─ 分析内容...
│  ├─ 生成过渡...
│  └─ 合成视频...
└─ 可取消操作 (30%)
```

**4. 结果页面 (Result Screen)**
```
布局：
├─ 视频预览 (60%)
│  ├─ 完整视频播放
│  ├─ 时间显示
│  └─ 质量指标
├─ 统计信息 (20%)
│  ├─ 原始时长
│  ├─ 编辑后时长
│  ├─ 压缩比
│  └─ 保存大小
└─ 操作按钮 (20%)
   ├─ 分享
   ├─ 保存
   ├─ 重新编辑
   └─ 返回
```

#### 2.3.3 交互规范

**手势操作**
```
操作          效果              备注
─────────────────────────────────
双击          播放/暂停         视频预览区
长按          显示上下文菜单     列表项
滑动          切换页面          底部导航
拖拽          调整时间          时间轴
捏合          缩放              预览

```

**反馈设计**
```
成功反馈：
- 振动 + 绿色勾选 + 弹窗
- 示例：编辑完成

加载反馈：
- 加载动画 + 进度文本
- 示例：视频处理中...

错误反馈：
- 红色提示 + 错误说明 + 重试按钮
- 示例：网络连接失败
```

#### 2.3.4 无障碍设计
```
支持项目：
- 屏幕阅读器 (TalkBack, VoiceOver)
- 大号字体设置
- 高对比度模式
- 语音输入
- 字幕和音频描述
```

---

## 3. API 集成指南

### 3.1 API 架构

**基础配置**
```dart
class ApiConfig {
  static const String baseUrl = 'https://api.video-ai.com';
  static const String baseUrlDev = 'http://localhost:8000';
  static const Duration timeout = Duration(seconds: 30);
  static const String apiVersion = '/v1';

  // 视频处理端点
  static const String uploadVideo = '/v1/videos/upload';
  static const String processVideo = '/v1/videos/process';
  static const String getProcessStatus = '/v1/videos/{videoId}/status';
  static const String downloadVideo = '/v1/videos/{videoId}/download';

  // 用户端点
  static const String getUserProfile = '/v1/users/me';
  static const String updateUserProfile = '/v1/users/me';
  static const String getUserHistory = '/v1/users/me/history';

  // 推荐端点
  static const String getRecommendations = '/v1/recommendations';
  static const String saveFeedback = '/v1/feedback';
}
```

### 3.2 视频处理流程

**Step 1: 视频上传**
```dart
Future<String> uploadVideo(File videoFile) async {
  final formData = FormData.fromMap({
    'file': await MultipartFile.fromFile(
      videoFile.path,
      filename: basename(videoFile.path),
    ),
  });

  final response = await dio.post(
    ApiConfig.uploadVideo,
    data: formData,
    onSendProgress: (int sent, int total) {
      // 更新上传进度 (0-100%)
      print('Uploaded: ${(sent/total*100).toStringAsFixed(0)}%');
    },
  );

  return response.data['videoId']; // 返回视频ID
}
```

**Step 2: 提交处理任务**
```dart
Future<String> submitProcessingJob({
  required String videoId,
  required List<String> interests,
  required String outputLength,
  String? language = 'en',
}) async {
  final response = await dio.post(
    ApiConfig.processVideo,
    data: {
      'videoId': videoId,
      'interests': interests,
      'outputLength': outputLength, // 'short', 'medium', 'long'
      'language': language,
      'preferences': {
        'transitionStyle': 'ai_generated',
        'includeSubtitles': true,
      }
    },
  );

  return response.data['jobId']; // 返回处理任务ID
}
```

**Step 3: 监听处理进度**
```dart
Stream<ProcessingStatus> watchProcessingStatus(String jobId) {
  return Stream.periodic(Duration(seconds: 2), (_) => jobId)
      .asyncMap((jobId) async {
        final response = await dio.get(
          ApiConfig.getProcessStatus.replaceAll('{videoId}', jobId),
        );
        return ProcessingStatus.fromJson(response.data);
      })
      .takeUntil(
        // 当状态为完成或失败时停止
        where((status) =>
          status.status == 'completed' || status.status == 'failed'
        ),
      );
}

// 使用示例
void startProcessing() {
  watchProcessingStatus(jobId).listen(
    (status) {
      print('Progress: ${status.progress}%');
      print('Current stage: ${status.currentStage}');
    },
    onError: (error) => print('Error: $error'),
    onDone: () => print('Processing completed'),
  );
}
```

**Step 4: 视频下载**
```dart
Future<File> downloadProcessedVideo(String videoId) async {
  final dir = await getApplicationDocumentsDirectory();
  final savePath = '${dir.path}/videos/${videoId}.mp4';

  await dio.download(
    ApiConfig.downloadVideo.replaceAll('{videoId}', videoId),
    savePath,
    onReceiveProgress: (received, total) {
      print('Download progress: ${(received/total*100).toStringAsFixed(0)}%');
    },
  );

  return File(savePath);
}
```

### 3.3 离线功能支持

**本地模型部署**
```dart
// 使用 TensorFlow Lite 加载本地模型
class LocalTranscriber {
  late Interpreter interpreter;

  Future<void> initialize() async {
    interpreter = await Interpreter.fromAsset(
      'assets/models/transcribe_lite.tflite',
    );
  }

  Future<String> transcribe(String audioPath) async {
    // 加载音频
    final audioData = await loadAudioFile(audioPath);

    // 本地转录
    final input = <List<List<num>>>[[audioData]];
    final output = <List<List<num>>>[];

    interpreter.run(input, output);

    return output[0][0].toString();
  }
}
```

**离线编辑模式**
```dart
class OfflineEditMode {
  // 缓存的用户兴趣和设置
  final List<String> cachedInterests;
  final Map<String, dynamic> cachedPreferences;

  // 本地视频处理
  Future<void> performLocalEditing({
    required File videoFile,
    required List<int> selectedSegments,
  }) async {
    // 1. 使用FFmpeg进行基本编辑
    // 2. 应用缓存的效果参数
    // 3. 生成临时视频
    // 4. 网络恢复后同步结果
  }

  // 数据同步
  Future<void> syncWithServer() async {
    // 上传本地编辑的视频
    // 获取云端AI处理结果
    // 合并结果
  }
}
```

### 3.4 数据同步策略

**同步模型**
```
┌─────────────┐
│ 本地存储    │ ◄────┐
└──────┬──────┘      │
       │             │
       ▼             │
┌─────────────┐      │
│ 待同步队列  │      │
└──────┬──────┘      │
       │             │
       ▼             │
┌─────────────┐      │
│ 云端服务器  │      │
└──────┬──────┘      │
       │             │
       └──────────────┘
           (拉取)
```

**实现**
```dart
class SyncManager {
  final localDatabase = LocalDatabase();
  final apiService = ApiService();

  Future<void> syncAll() async {
    // 1. 上传本地编辑
    await uploadLocalEdits();

    // 2. 下载云端更新
    await downloadCloudUpdates();

    // 3. 解决冲突
    await resolveConflicts();

    // 4. 清理本地缓存
    await cleanupCache();
  }

  Future<void> smartSync() {
    // 仅在WiFi + 充电时同步大文件
    return Connectivity().onConnectivityChanged
        .where((result) => result == ConnectivityResult.wifi)
        .asyncMap((_) async {
          if (await isBatteryCharging()) {
            await syncAll();
          }
        })
        .listen((_) {});
  }
}
```

---

## 4. 性能优化

### 4.1 视频处理优化

**编码优化**
```dart
// 使用硬件加速编码
class VideoOptimizer {
  // 根据设备性能选择编码器
  String selectEncoder() {
    if (Platform.isIOS) {
      return 'videotoolbox'; // iOS硬件编码
    } else {
      return 'h264_mediacodec'; // Android硬件编码
    }
  }

  // 动态调整比特率
  int selectBitrate(int originalBitrate) {
    final deviceMemory = getDeviceMemory();
    if (deviceMemory < 2048) {
      return (originalBitrate * 0.5).toInt(); // 4GB以下设备
    }
    return originalBitrate;
  }

  // 分辨率自适应
  Size selectResolution(Size originalSize) {
    final screenSize = MediaQuery.of(context).size;
    if (originalSize.width > screenSize.width * 2) {
      return Size(
        screenSize.width * 2,
        screenSize.height * 2,
      );
    }
    return originalSize;
  }
}
```

**缓存策略**
```dart
class CacheManager {
  // 三层缓存架构

  // L1: 内存缓存 (最快，容量小)
  final LruCache<String, VideoFrame> memoryCache = LruCache(5);

  // L2: 磁盘缓存 (中等，容量中等)
  final DiskLruCache diskCache = DiskLruCache('video_cache', 500 * 1024 * 1024); // 500MB

  // L3: 网络缓存 (最慢，容量大)
  final remoteCache = RemoteCache();

  Future<VideoFrame?> getFrame(String videoId, int frameNumber) async {
    // 查询L1
    if (memoryCache.containsKey(videoId)) {
      return memoryCache.get(videoId);
    }

    // 查询L2
    if (await diskCache.contains(videoId)) {
      final frame = await diskCache.get(videoId);
      memoryCache.put(videoId, frame); // 回源到L1
      return frame;
    }

    // 查询L3
    final frame = await remoteCache.fetchFrame(videoId, frameNumber);
    diskCache.put(videoId, frame); // 缓存到L2
    memoryCache.put(videoId, frame); // 缓存到L1

    return frame;
  }
}
```

### 4.2 网络优化

**智能网络管理**
```dart
class SmartNetworkManager {
  // 根据网络类型调整策略
  Future<void> adjustStrategy() async {
    final connectivity = Connectivity();
    final connection = await connectivity.checkConnectivity();

    switch (connection) {
      case ConnectivityResult.mobile:
        // 使用4G: 降低分辨率，压缩视频
        videoQuality = 'low';
        break;
      case ConnectivityResult.wifi:
        // 使用WiFi: 全质量上传
        videoQuality = 'high';
        break;
      case ConnectivityResult.none:
        // 无网络: 使用离线模式
        enableOfflineMode();
        break;
    }
  }

  // 断点续传
  Future<void> resumableUpload(File videoFile) async {
    const chunkSize = 5 * 1024 * 1024; // 5MB chunks
    int uploadedBytes = 0;

    final chunks = await divideIntoChunks(videoFile, chunkSize);

    for (final chunk in chunks) {
      while (true) {
        try {
          await uploadChunk(chunk, uploadedBytes);
          uploadedBytes += chunk.lengthSync();
          break;
        } catch (e) {
          // 重试逻辑，使用指数退避
          await Future.delayed(Duration(seconds: pow(2, retryCount).toInt()));
        }
      }
    }
  }
}
```

**请求优化**
```dart
class RequestOptimizer {
  // 请求聚合 - 减少API调用数
  final _requestBuffer = <Future>[];

  void batchRequests(Future request) {
    _requestBuffer.add(request);

    if (_requestBuffer.length >= 10) {
      flushBatch();
    }
  }

  Future<void> flushBatch() async {
    final requests = _requestBuffer.toList();
    _requestBuffer.clear();
    await Future.wait(requests);
  }

  // 请求去重
  final _requestCache = <String, Future>{};

  Future<T> cachedRequest<T>(String key, Future<T> Function() request) {
    if (_requestCache.containsKey(key)) {
      return _requestCache[key] as Future<T>;
    }

    final future = request();
    _requestCache[key] = future;

    return future;
  }

  // 请求优先级队列
  final PriorityQueue requestQueue = PriorityQueue((a, b) {
    return a.priority.compareTo(b.priority); // 优先级高的先执行
  });
}
```

### 4.3 电池和存储优化

**电池优化**
```dart
class BatteryOptimizer {
  // 监听电池状态
  void optimizeForBattery() {
    Battery().onBatteryStateChanged.listen((state) {
      switch (state) {
        case BatteryState.full:
          // 充电完整：运行重型处理
          enableHighPerformance();
          break;
        case BatteryState.charging:
          // 充电中：运行后台同步
          enableBackgroundSync();
          break;
        case BatteryState.discharging:
          // 放电中：降低性能，省电模式
          enablePowerSavingMode();
          break;
        case BatteryState.unknown:
          enableBalancedMode();
          break;
      }
    });
  }

  // 降低帧率
  void reduceFPS() {
    // 预览: 30fps → 15fps
    // 处理: 60fps → 30fps
  }

  // 减少背光时间
  void reduceBrightness() {
    final screen = DeviceInfoPlus().deviceInfo;
    // 根据环境光自动调整亮度
  }
}
```

**存储优化**
```dart
class StorageManager {
  static const MAX_CACHE = 500 * 1024 * 1024; // 500MB

  Future<void> manageStorage() async {
    final dir = await getApplicationCacheDirectory();
    final cacheSize = await calculateDirSize(dir);

    if (cacheSize > MAX_CACHE) {
      // 删除最旧的文件
      await deleteLRUFiles(dir, cacheSize - MAX_CACHE);
    }
  }

  // 使用App Groups (iOS) / Scoped Storage (Android)
  Future<Directory> getSharedStorageDirectory() async {
    if (Platform.isIOS) {
      return Directory('/var/mobile/Containers/Shared/AppGroup/group.com.videoai');
    } else {
      return getExternalFilesDirectory(null);
    }
  }

  // 智能压缩
  Future<File> compressVideo(File videoFile) async {
    // 使用FFmpeg进行H.265编码（文件大小减少30-50%）
    final cmd = [
      '-i', videoFile.path,
      '-c:v', 'libx265',
      '-crf', '28',
      '-c:a', 'aac',
      '-b:a', '128k',
      outputPath,
    ];

    return await FFmpegKit.executeWithArguments(cmd);
  }
}
```

---

## 5. 开发路线图

### Phase 1: MVP (3个月)
- [x] 基础框架搭建
- [x] 视频导入与预览
- [x] API集成（上传、处理、下载）
- [x] 基础编辑功能
- [x] 本地存储

### Phase 2: 功能增强 (2个月)
- [ ] 高级编辑工具
- [ ] 离线编辑模式
- [ ] 推送通知
- [ ] 性能优化

### Phase 3: 社交分享 (2个月)
- [ ] 多平台分享
- [ ] 用户反馈系统
- [ ] 社交功能

### Phase 4: 推荐系统 (3个月)
- [ ] 用户画像
- [ ] 推荐引擎
- [ ] 内容发现

---

## 6. 测试策略

### 6.1 单元测试
```dart
void main() {
  test('API client should handle errors', () async {
    // Mock HTTP响应
    final client = MockHttpClient();
    client.expectRequest(
      method: 'POST',
      url: Uri.parse('${ApiConfig.baseUrl}${ApiConfig.processVideo}'),
      responseStatus: 400,
      responseBody: '{"error": "Invalid video"}',
    );

    final api = ApiService(client: client);
    expect(
      () => api.processVideo(videoId: 'invalid'),
      throwsException,
    );
  });
}
```

### 6.2 集成测试
```dart
void main() {
  group('Video Processing Flow', () {
    testWidgets('Complete flow from upload to download', (tester) async {
      await tester.pumpWidget(VideoEditorApp());

      // 导入视频
      await tester.tap(find.byType(ImportVideoButton));
      await tester.pumpAndSettle();

      // 选择参数
      await tester.tap(find.byTooltip('兴趣标签'));
      await tester.pumpAndSettle();

      // 开始处理
      await tester.tap(find.byType(ProcessButton));
      await tester.pumpAndSettle(Duration(seconds: 30));

      // 验证结果
      expect(find.byType(VideoPreview), findsOneWidget);
    });
  });
}
```

### 6.3 性能测试
```dart
Future<void> measureVideoUploadPerformance() async {
  final stopwatch = Stopwatch()..start();

  final videoFile = await generateTestVideo(size: 100 * 1024 * 1024);
  await apiService.uploadVideo(videoFile);

  stopwatch.stop();

  print('Upload time: ${stopwatch.elapsedMilliseconds}ms');
  print('Upload speed: ${(100 / (stopwatch.elapsedMilliseconds / 1000)) / 1024}MB/s');

  // 验证性能指标
  expect(stopwatch.elapsedMilliseconds, lessThan(60000)); // < 1分钟
}
```

---

## 总结

本文档提供了Video-AI移动端应用的完整架构方案，包括：
- 推荐使用Flutter框架
- 完整的功能设计与优先级规划
- 详细的API集成指南
- 全面的性能优化策略
- 清晰的开发路线图

通过遵循本文档的建议，可以快速高效地构建高质量的移动端应用。
