# Video-AI 开发者指南

本指南面向希望参与 Video-AI 项目开发、扩展功能或集成到自己项目中的开发者。

---

## 目录

1. [开发环境搭建](#开发环境搭建)
2. [代码结构说明](#代码结构说明)
3. [核心模块API](#核心模块api)
4. [如何添加新功能](#如何添加新功能)
5. [测试指南](#测试指南)
6. [代码规范](#代码规范)
7. [贡献流程](#贡献流程)

---

## 开发环境搭建

### 1. 克隆项目

```bash
git clone <repository-url>
cd video-ai
```

### 2. 创建开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发工具

# 安装预提交钩子
pre-commit install
```

### 3. 配置开发工具

**VS Code 推荐设置** (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

**PyCharm配置**:
- 启用Black格式化
- 配置pytest作为测试运行器
- 启用类型检查

### 4. 运行测试验证

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_llm_factory.py -v

# 生成覆盖率报告
pytest --cov=src tests/
```

---

## 代码结构说明

### 项目架构

```
video-ai/
├── src/                    # 源代码
│   ├── core/              # 核心功能模块
│   ├── services/          # 业务服务层
│   ├── models/            # 数据模型
│   └── utils/             # 工具函数
├── tests/                 # 测试代码
├── examples/              # 示例和UI
├── docs/                  # 文档
└── data/                  # 数据目录
```

### 核心模块详解

#### 1. `src/core/` - 核心功能

**transcriber.py** - 视频转录
```python
class VideoTranscriber:
    """视频转录器，使用Whisper模型"""
    def transcribe(self, video_path: str) -> Dict:
        """转录视频，返回文本和时间戳"""
```

**analyzer.py** - 内容分析
```python
class ContentAnalyzer:
    """内容分析器，支持LLM和NLP两种模式"""
    def analyze(self, transcript: str, user_interests: List[str]) -> Dict:
        """分析转录内容，提取相关片段"""
```

**editor.py** - 视频编辑
```python
class VideoEditor:
    """视频编辑器，执行剪辑和拼接"""
    def edit_video(self, input_path: str, output_path: str) -> Dict:
        """编辑视频，返回处理结果"""
```

**llm_factory.py** - LLM工厂
```python
class LLMFactory:
    """LLM工厂，统一创建不同的LLM提供商"""
    @staticmethod
    def create(provider: str, api_key: str, **kwargs) -> LLMProvider:
        """创建LLM实例"""
```

#### 2. `src/services/` - 业务服务

**personalization.py** - 个性化服务
```python
class PersonalizationService:
    """个性化服务，管理用户画像和推荐"""
    def create_user_profile(self, user_id: str, initial_interests: List[str]):
        """创建用户画像"""

    def track_user_action(self, user_id: str, action: str, video_id: str, **kwargs):
        """追踪用户行为"""
```

**realtime_recommendation.py** - 实时推荐
```python
class RealtimeRecommendationEngine:
    """实时推荐引擎"""
    def track_behavior(self, user_id: str, action: str, video_id: str, **kwargs):
        """追踪行为"""

    def get_recommendations(self, user_id: str, num: int = 10) -> List[Dict]:
        """获取推荐"""
```

#### 3. `src/models/` - 数据模型

**user_profile.py** - 用户画像
```python
class UserProfile:
    """用户画像模型"""
    def __init__(self, user_id: str, interests: List[str], **kwargs):
        self.user_id = user_id
        self.interests = interests
        # ... 其他属性
```

---

## 核心模块API

### VideoEditor API

#### 初始化

```python
from src.core.editor import VideoEditor

editor = VideoEditor(
    user_interests: List[str],        # 用户兴趣标签
    skip_topics: List[str] = None,    # 跳过的主题
    output_length: str = "medium",     # short/medium/long
    pace: str = "normal",              # slow/normal/fast
    transition_style: str = "text",    # text/fade/blur/zoom/ai_generated
    use_llm: bool = False,             # 是否使用LLM
    llm_provider: str = "openai",      # openai/gemini/claude
    quality_threshold: float = 5.0     # 质量阈值 (1-10)
)
```

#### 主要方法

```python
# 编辑视频
result = editor.edit_video(
    input_path: str,                   # 输入视频路径
    output_path: str                   # 输出视频路径
) -> Dict[str, Any]

# 返回结果
{
    'success': bool,                   # 是否成功
    'output_path': str,                # 输出路径
    'original_duration': float,        # 原始时长(秒)
    'edited_duration': float,          # 编辑后时长(秒)
    'compression_ratio': float,        # 压缩率
    'segments_included': int,          # 包含片段数
    'processing_time': float           # 处理时间(秒)
}
```

### LLMFactory API

#### 创建LLM实例

```python
from src.core.llm_factory import LLMFactory

# OpenAI
llm = LLMFactory.create(
    provider="openai",
    api_key="sk-...",
    model="gpt-4"
)

# Gemini
llm = LLMFactory.create(
    provider="gemini",
    api_key="...",
    model="gemini-pro"
)

# Claude
llm = LLMFactory.create(
    provider="claude",
    api_key="...",
    model="claude-3-sonnet-20240229"
)
```

#### 使用LLM

```python
# 文本生成
response = await llm.generate(
    prompt="分析这段视频内容...",
    max_tokens=1000,
    temperature=0.7
)

# JSON生成
result = await llm.generate_json(
    prompt="提取视频主题...",
    schema={
        "type": "object",
        "properties": {
            "topics": {"type": "array"},
            "summary": {"type": "string"}
        }
    }
)
```

### PersonalizationService API

```python
from src.services.personalization import PersonalizationService

service = PersonalizationService(enable_realtime=True)

# 创建用户
service.create_user_profile(
    user_id="user_001",
    initial_interests=["AI", "机器学习"]
)

# 追踪行为
service.track_user_action(
    user_id="user_001",
    action="view",          # view/like/dislike/share/skip
    video_id="video_001",
    duration=600            # 观看时长(秒)
)

# 获取推荐
recommendations = service.get_realtime_recommendations(
    user_id="user_001",
    num=5
)
```

---

## 如何添加新功能

### 示例：添加新的过渡效果

#### 1. 在 TransitionGenerator 中添加方法

```python
# src/core/generator.py

class TransitionGenerator:
    def create_custom_transition(
        self,
        text: str,
        duration: float = 3.0,
        style: str = "custom"
    ) -> str:
        """创建自定义过渡效果"""

        # 1. 创建视频片段
        clip = TextClip(
            text,
            fontsize=70,
            color='white',
            bg_color='blue',
            size=(1920, 1080)
        ).set_duration(duration)

        # 2. 添加自定义效果
        clip = clip.fx(vfx.fadeout, 0.5)

        # 3. 保存
        output_path = f"transitions/custom_{int(time.time())}.mp4"
        clip.write_videofile(output_path, fps=30)

        return output_path
```

#### 2. 在 VideoEditor 中集成

```python
# src/core/editor.py

class VideoEditor:
    def _add_transitions(self, clips: List) -> List:
        """添加过渡效果"""
        if self.transition_style == "custom":
            return self._add_custom_transitions(clips)
        # ... 其他逻辑

    def _add_custom_transitions(self, clips: List) -> List:
        """添加自定义过渡"""
        generator = TransitionGenerator()
        new_clips = []

        for i, clip in enumerate(clips):
            new_clips.append(clip)
            if i < len(clips) - 1:
                transition = generator.create_custom_transition(
                    text=f"接下来: 片段{i+2}",
                    style="custom"
                )
                new_clips.append(VideoFileClip(transition))

        return new_clips
```

#### 3. 添加测试

```python
# tests/test_generator.py

def test_custom_transition(temp_dir):
    """测试自定义过渡"""
    generator = TransitionGenerator()

    result = generator.create_custom_transition(
        text="测试过渡",
        duration=3.0,
        style="custom"
    )

    assert os.path.exists(result)
    assert result.endswith(".mp4")
```

#### 4. 更新文档

在 `docs/USER_MANUAL.md` 中添加新功能说明。

---

## 测试指南

### 测试结构

```
tests/
├── test_integration.py      # 集成测试
├── test_performance.py       # 性能测试
├── test_llm_factory.py       # LLM工厂测试
├── test_nlp_processor.py     # NLP处理器测试
└── ...                       # 其他单元测试
```

### 编写测试

#### 单元测试模板

```python
import pytest
from unittest.mock import Mock, patch

def test_feature_name():
    """测试功能描述"""
    # Arrange - 准备
    input_data = "test input"
    expected_output = "expected result"

    # Act - 执行
    result = function_to_test(input_data)

    # Assert - 断言
    assert result == expected_output
```

#### 使用 Fixtures

```python
@pytest.fixture
def temp_dir(tmp_path):
    """临时目录"""
    return str(tmp_path)

@pytest.fixture
def mock_llm():
    """模拟LLM"""
    llm = Mock()
    llm.generate.return_value = "mocked response"
    return llm

def test_with_fixtures(temp_dir, mock_llm):
    """使用fixtures的测试"""
    # 使用temp_dir和mock_llm
    pass
```

#### 异步测试

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """测试异步函数"""
    result = await async_function()
    assert result is not None
```

### 运行测试

```bash
# 所有测试
pytest tests/ -v

# 特定文件
pytest tests/test_llm_factory.py -v

# 特定测试
pytest tests/test_llm_factory.py::test_create_openai -v

# 并行执行
pytest tests/ -n 4

# 覆盖率
pytest --cov=src --cov-report=html tests/
```

### Mock 和 Patch

```python
from unittest.mock import Mock, patch, MagicMock

# Mock对象
mock_obj = Mock()
mock_obj.method.return_value = "result"

# Patch装饰器
@patch('module.ClassName')
def test_with_patch(mock_class):
    mock_class.return_value.method.return_value = "result"
    # 测试代码

# Patch上下文管理器
def test_with_context():
    with patch('module.function') as mock_func:
        mock_func.return_value = "result"
        # 测试代码
```

---

## 代码规范

### Python 风格指南

遵循 [PEP 8](https://pep8.org/) 风格指南。

#### 命名规范

```python
# 类名：大驼峰
class VideoEditor:
    pass

# 函数/变量：小写+下划线
def process_video(input_path: str) -> Dict:
    user_interests = ["AI"]
    return {}

# 常量：全大写
MAX_VIDEO_LENGTH = 3600
DEFAULT_QUALITY = 7.0

# 私有方法/变量：单下划线开头
def _internal_method(self):
    self._private_var = "value"
```

#### 类型注解

```python
from typing import List, Dict, Optional, Union

def analyze_content(
    text: str,
    interests: List[str],
    threshold: float = 0.5
) -> Dict[str, any]:
    """分析内容相关性"""
    pass

class UserProfile:
    def __init__(
        self,
        user_id: str,
        interests: List[str],
        metadata: Optional[Dict] = None
    ):
        self.user_id: str = user_id
        self.interests: List[str] = interests
```

#### 文档字符串

```python
def process_video(
    input_path: str,
    output_path: str,
    user_interests: List[str]
) -> Dict[str, Any]:
    """
    处理视频，根据用户兴趣进行智能剪辑。

    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        user_interests: 用户兴趣标签列表

    Returns:
        包含处理结果的字典，包括：
        - success: 是否成功
        - output_path: 输出路径
        - duration: 处理时长

    Raises:
        FileNotFoundError: 输入文件不存在
        ValueError: 参数无效

    Example:
        >>> result = process_video("input.mp4", "output.mp4", ["AI"])
        >>> print(result['success'])
        True
    """
    pass
```

### 代码质量工具

#### Black (代码格式化)

```bash
# 格式化所有文件
black src/ tests/

# 检查但不修改
black --check src/

# 配置文件 pyproject.toml
[tool.black]
line-length = 100
target-version = ['py38']
```

#### Pylint (代码检查)

```bash
# 检查代码
pylint src/

# 配置文件 .pylintrc
[MASTER]
max-line-length=100
disable=C0111,R0903
```

#### mypy (类型检查)

```bash
# 类型检查
mypy src/

# 配置文件 mypy.ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
```

---

## 贡献流程

### 1. Fork 和 Clone

```bash
# Fork 项目到你的账号
# 然后 clone
git clone https://github.com/your-username/video-ai.git
cd video-ai

# 添加上游仓库
git remote add upstream https://github.com/original/video-ai.git
```

### 2. 创建分支

```bash
# 从main创建新分支
git checkout -b feature/your-feature-name

# 或修复bug
git checkout -b fix/bug-description
```

### 3. 开发和测试

```bash
# 进行开发
# ...

# 运行测试
pytest tests/ -v

# 运行代码检查
black src/ tests/
pylint src/
mypy src/
```

### 4. 提交更改

```bash
# 添加更改
git add .

# 提交（遵循提交信息规范）
git commit -m "feat: add custom transition support"

# 或
git commit -m "fix: resolve YouTube download timeout issue"
```

#### 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具

**示例**:
```
feat(editor): add custom transition support

- Add create_custom_transition method
- Integrate with VideoEditor
- Add tests and documentation

Closes #123
```

### 5. 推送和PR

```bash
# 推送到你的fork
git push origin feature/your-feature-name

# 在GitHub上创建Pull Request
```

### 6. Code Review

- 响应reviewer的评论
- 根据反馈修改代码
- 保持PR更新

---

## 开发最佳实践

### 1. 模块化设计

- 单一职责原则
- 低耦合高内聚
- 接口抽象

### 2. 错误处理

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    # 处理或重新抛出
    raise
finally:
    cleanup()
```

### 3. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

def process():
    logger.info("Starting process")
    try:
        # 处理
        logger.debug("Debug info")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
```

### 4. 配置管理

```python
# 使用配置文件而不是硬编码
config = load_config("config.yaml")
api_key = config.get("openai.api_key")
```

### 5. 性能优化

- 使用异步IO
- 缓存expensive操作
- 批量处理
- GPU加速

---

## 有用的资源

### 文档
- [Python官方文档](https://docs.python.org/3/)
- [FFmpeg文档](https://ffmpeg.org/documentation.html)
- [MoviePy文档](https://zulko.github.io/moviepy/)

### 工具
- [pytest文档](https://docs.pytest.org/)
- [Black](https://black.readthedocs.io/)
- [Pylint](https://pylint.org/)

### 社区
- GitHub Discussions
- Discord服务器
- Stack Overflow

---

## 获取帮助

- 查看[API参考](API_REFERENCE.md)
- 查看[用户手册](USER_MANUAL.md)
- 提交[GitHub Issue](https://github.com/yourusername/video-ai/issues)
- 加入[Discord](https://discord.gg/video-ai)

---

**Happy Coding! 🚀**
