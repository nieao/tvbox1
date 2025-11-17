# A/B 测试框架 API 参考

## 导入

```python
from src.services.ab_testing import (
    ABTestingFramework,
    ABExperiment,
    ABTestResult,
    ExperimentStatus,
    VideoEditorABTesting,
    MetricData
)
```

## ABTestingFramework

主要的 A/B 测试框架类，提供实验管理和分析功能。

### 初始化

```python
framework = ABTestingFramework(storage_dir: str = "data/ab_tests")
```

**参数:**
- `storage_dir` (str): 数据存储目录，默认为 "data/ab_tests"

**属性:**
- `experiments`: Dict[str, ABExperiment] - 实验缓存
- `user_assignments`: Dict[str, Dict[str, str]] - 用户分配记录
- `metrics_data`: 指标数据存储
- `analysis_cache`: 分析结果缓存

### 方法

#### create_experiment

创建新的 A/B 测试实验。

```python
def create_experiment(
    experiment_id: str,
    name: str,
    description: str,
    variants: Dict[str, Dict],
    traffic_split: Optional[Dict[str, float]] = None,
    metrics: Optional[List[str]] = None,
    tags: Optional[Dict[str, Any]] = None
) -> ABExperiment:
```

**参数:**
- `experiment_id` (str): 实验的唯一标识符
- `name` (str): 实验名称（显示用）
- `description` (str): 实验描述
- `variants` (Dict[str, Dict]): 变体配置字典，格式 {variant_name: config_dict}
- `traffic_split` (Optional[Dict[str, float]]): 流量分配比例，总和必须为 1.0。默认为均匀分配
- `metrics` (Optional[List[str]]): 要收集的指标列表。默认为常见指标
- `tags` (Optional[Dict[str, Any]]): 实验标签/元数据

**返回:**
- ABExperiment: 创建的实验对象

**示例:**
```python
experiment = framework.create_experiment(
    experiment_id='exp_001',
    name='用户界面优化',
    description='测试新的用户界面设计',
    variants={
        'control': {'ui_version': 'v1.0'},
        'variant_a': {'ui_version': 'v2.0'},
        'variant_b': {'ui_version': 'v2.1'}
    },
    traffic_split={'control': 0.5, 'variant_a': 0.25, 'variant_b': 0.25},
    metrics=['click_rate', 'conversion_rate', 'user_satisfaction'],
    tags={'owner': 'design_team', 'priority': 'high'}
)
```

---

#### start_experiment

启动实验（将状态从 DRAFT 改为 RUNNING）。

```python
def start_experiment(experiment_id: str) -> ABExperiment:
```

**参数:**
- `experiment_id` (str): 实验 ID

**返回:**
- ABExperiment: 更新后的实验对象

**异常:**
- ValueError: 实验不存在

**示例:**
```python
framework.start_experiment('exp_001')
```

---

#### pause_experiment

暂停正在进行的实验。

```python
def pause_experiment(experiment_id: str) -> ABExperiment:
```

**参数:**
- `experiment_id` (str): 实验 ID

**返回:**
- ABExperiment: 更新后的实验对象

---

#### stop_experiment

停止实验（改为 COMPLETED 状态）。

```python
def stop_experiment(experiment_id: str) -> ABExperiment:
```

**参数:**
- `experiment_id` (str): 实验 ID

**返回:**
- ABExperiment: 更新后的实验对象

---

#### assign_variant

为用户分配实验变体。同一用户始终被分配到同一变体。

```python
def assign_variant(
    user_id: str,
    experiment_id: str,
    seed: Optional[int] = None
) -> str:
```

**参数:**
- `user_id` (str): 用户 ID
- `experiment_id` (str): 实验 ID
- `seed` (Optional[int]): 随机种子（用于可重现的分配，仅在测试时使用）

**返回:**
- str: 分配的变体名称

**异常:**
- ValueError: 实验不存在

**示例:**
```python
variant = framework.assign_variant('user_123', 'exp_001')
print(f"用户被分配到: {variant}")  # 输出: "variant_a"
```

---

#### record_metric

记录单个用户的指标数据。

```python
def record_metric(
    user_id: str,
    experiment_id: str,
    metric_name: str,
    value: float,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
```

**参数:**
- `user_id` (str): 用户 ID
- `experiment_id` (str): 实验 ID
- `metric_name` (str): 指标名称
- `value` (float): 指标值
- `metadata` (Optional[Dict[str, Any]]): 额外的元数据

**返回:**
- bool: 是否成功记录（失败可能是用户未被分配）

**示例:**
```python
# 记录完成率
framework.record_metric(
    'user_123',
    'exp_001',
    'completion_rate',
    0.85,
    metadata={'duration': 120}
)

# 记录用户评分
framework.record_metric('user_123', 'exp_001', 'user_rating', 4.5)
```

---

#### analyze_experiment

分析实验的统计结果。

```python
def analyze_experiment(
    experiment_id: str,
    metric_name: str,
    control_variant: str,
    use_cache: bool = True
) -> Dict[str, Any]:
```

**参数:**
- `experiment_id` (str): 实验 ID
- `metric_name` (str): 要分析的指标名称
- `control_variant` (str): 对照组变体名称（用于计算相对改进）
- `use_cache` (bool): 是否使用缓存，默认为 True

**返回:**
Dict 包含:
```python
{
    'experiment_id': str,
    'metric': str,
    'control': str,
    'timestamp': str,
    'results': {
        'variant_name': {
            'mean': float,           # 平均值
            'std': float,            # 标准差
            'min': float,            # 最小值
            'max': float,            # 最大值
            'median': float,         # 中位数
            'count': int,            # 样本数
            'values': List[float],   # 所有值
            'improvement': float,    # 相对改进百分比 (仅非对照组)
            'p_value': float,        # p 值 (仅非对照组)
            'significant': bool,     # 统计显著 (仅非对照组)
            'confidence_interval': float  # 95% CI (仅非对照组)
        }
    }
}
```

**示例:**
```python
analysis = framework.analyze_experiment(
    'exp_001',
    'completion_rate',
    'control'
)

for variant, result in analysis['results'].items():
    print(f"{variant}: {result['mean']:.4f} ± {result['std']:.4f}")
```

---

#### compare_variants

对比多个变体（使用 ANOVA）。

```python
def compare_variants(
    experiment_id: str,
    metric_name: str,
    variants: List[str]
) -> Dict[str, Any]:
```

**参数:**
- `experiment_id` (str): 实验 ID
- `metric_name` (str): 指标名称
- `variants` (List[str]): 要对比的变体列表

**返回:**
Dict 包含统计结果和 ANOVA 分析

**示例:**
```python
result = framework.compare_variants(
    'exp_001',
    'user_rating',
    ['control', 'variant_a', 'variant_b']
)

if 'anova' in result['results']:
    anova = result['results']['anova']
    print(f"F-statistic: {anova['f_statistic']:.4f}")
    print(f"p-value: {anova['p_value']:.6f}")
```

---

#### generate_report

生成详细的 A/B 测试报告。

```python
def generate_report(
    experiment_id: str,
    control_variant: str
) -> str:
```

**参数:**
- `experiment_id` (str): 实验 ID
- `control_variant` (str): 对照组变体名称

**返回:**
- str: 格式化的报告文本

**示例:**
```python
report = framework.generate_report('exp_001', 'control')
print(report)

# 保存报告
with open('report.txt', 'w') as f:
    f.write(report)
```

---

#### export_data

导出实验数据。

```python
def export_data(
    experiment_id: str,
    output_format: str = "json"
) -> str:
```

**参数:**
- `experiment_id` (str): 实验 ID
- `output_format` (str): 输出格式，"json" 或 "csv"

**返回:**
- str: 格式化的数据

**示例:**
```python
# 导出为 JSON
json_data = framework.export_data('exp_001', output_format='json')
with open('data.json', 'w') as f:
    f.write(json_data)

# 导出为 CSV
csv_data = framework.export_data('exp_001', output_format='csv')
with open('data.csv', 'w') as f:
    f.write(csv_data)
```

---

#### get_experiment_summary

获取实验摘要信息。

```python
def get_experiment_summary(experiment_id: str) -> Dict[str, Any]:
```

**参数:**
- `experiment_id` (str): 实验 ID

**返回:**
Dict 包含:
```python
{
    'experiment_id': str,
    'name': str,
    'status': str,
    'variants': List[str],
    'total_users': int,
    'variant_distribution': Dict[str, int],  # {variant: user_count}
    'metrics': Dict[str, int]  # {metric: data_point_count}
}
```

**示例:**
```python
summary = framework.get_experiment_summary('exp_001')
print(f"总用户数: {summary['total_users']}")
print(f"变体分布: {summary['variant_distribution']}")
```

---

#### load_experiment

加载持久化的实验配置。

```python
def load_experiment(experiment_id: str) -> Optional[ABExperiment]:
```

**参数:**
- `experiment_id` (str): 实验 ID

**返回:**
- Optional[ABExperiment]: 实验对象，不存在则返回 None

---

#### list_experiments

列出所有已创建的实验 ID。

```python
def list_experiments() -> List[str]:
```

**返回:**
- List[str]: 实验 ID 列表

---

#### get_experiment

获取实验对象。

```python
def get_experiment(experiment_id: str) -> Optional[ABExperiment]:
```

**参数:**
- `experiment_id` (str): 实验 ID

**返回:**
- Optional[ABExperiment]: 实验对象

---

## VideoEditorABTesting

视频编辑器与 A/B 测试框架的集成类。

### 初始化

```python
editor_ab = VideoEditorABTesting(ab_framework: ABTestingFramework)
```

**参数:**
- `ab_framework` (ABTestingFramework): ABTestingFramework 实例

### 方法

#### set_experiment

设置当前实验和用户。

```python
def set_experiment(
    experiment_id: str,
    user_id: str
) -> str:
```

**参数:**
- `experiment_id` (str): 实验 ID
- `user_id` (str): 用户 ID

**返回:**
- str: 分配的变体名称

**示例:**
```python
variant = editor_ab.set_experiment('exp_001', 'user_123')
print(f"用户在实验中的变体: {variant}")
```

---

#### record_metric

记录指标（简化版本，不需要指定 user_id 和 experiment_id）。

```python
def record_metric(
    metric_name: str,
    value: float,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
```

**参数:**
- `metric_name` (str): 指标名称
- `value` (float): 指标值
- `metadata` (Optional[Dict[str, Any]]): 额外元数据

**返回:**
- bool: 是否成功

**示例:**
```python
editor_ab.record_metric('completion_rate', 0.85)
editor_ab.record_metric('watch_time', 300, metadata={'duration': 300})
```

---

#### get_variant_config

获取当前用户的变体配置。

```python
def get_variant_config() -> Optional[Dict]:
```

**返回:**
- Optional[Dict]: 变体配置，如果未设置实验则返回 None

**示例:**
```python
config = editor_ab.get_variant_config()
if config:
    print(f"变体配置: {config}")
```

---

## ABExperiment 数据类

表示一个 A/B 测试实验。

### 属性

```python
@dataclass
class ABExperiment:
    experiment_id: str
    name: str
    description: str
    variants: Dict[str, Dict]
    traffic_split: Dict[str, float]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = ExperimentStatus.DRAFT
    metrics: List[str] = ...
    created_at: datetime = ...
    tags: Dict[str, Any] = ...
```

### 方法

#### to_dict

转换为字典。

```python
def to_dict(self) -> Dict:
```

---

## ExperimentStatus 枚举

实验状态。

```python
class ExperimentStatus(str, Enum):
    DRAFT = "draft"           # 草稿
    RUNNING = "running"       # 运行中
    PAUSED = "paused"         # 暂停
    COMPLETED = "completed"   # 已完成
    STOPPED = "stopped"       # 已停止
```

---

## 错误处理

### 常见异常

```python
# 实验不存在
try:
    framework.start_experiment('nonexistent')
except ValueError as e:
    print(f"错误: {e}")

# 流量分配无效
try:
    framework.create_experiment(
        'exp_001',
        'test',
        'test',
        {'a': {}, 'b': {}},
        traffic_split={'a': 0.3, 'b': 0.3}  # 总和不是 1.0
    )
except ValueError as e:
    print(f"流量分配错误: {e}")
```

---

## 性能考虑

### 内存使用

- 每个数据点约占 100-200 字节内存
- 对于 10,000 用户 × 5 个变体 × 4 个指标 = 200,000 数据点，约需 20-40 MB 内存

### 分析性能

- 简单分析（平均值、标准差）: < 1ms
- t-test 分析: 1-10ms（取决于样本量）
- ANOVA 分析: 5-50ms

### 优化建议

```python
# 1. 使用缓存（默认启用）
# 2. 定期导出和清理过期数据
# 3. 对大数据集使用样本

# 样本分析（如果数据太多）
import random
sampled_users = random.sample(list(framework.user_assignments.keys()), 1000)
```

---

## 完整示例

参见 `/home/user/tvbox1/video-ai/examples/ab_test_demo.py` 和 `/home/user/tvbox1/video-ai/examples/ab_test_advanced_demo.py`
