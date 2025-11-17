"""
A/B 测试框架

提供完整的实验管理、流量分配、指标收集、统计分析等功能。
"""

import random
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import numpy as np

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """实验状态"""
    DRAFT = "draft"  # 草稿
    RUNNING = "running"  # 运行中
    PAUSED = "paused"  # 暂停
    COMPLETED = "completed"  # 已完成
    STOPPED = "stopped"  # 已停止


@dataclass
class ABExperiment:
    """A/B 测试实验"""
    experiment_id: str
    name: str
    description: str
    variants: Dict[str, Dict]  # variant_name -> config
    traffic_split: Dict[str, float]  # variant_name -> percentage
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = ExperimentStatus.DRAFT
    metrics: List[str] = field(default_factory=lambda: [
        'completion_rate',
        'user_rating',
        'watch_time',
        'engagement_score'
    ])
    created_at: datetime = field(default_factory=datetime.now)
    tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """转换为字典"""
        d = asdict(self)
        d['start_time'] = self.start_time.isoformat() if self.start_time else None
        d['end_time'] = self.end_time.isoformat() if self.end_time else None
        d['created_at'] = self.created_at.isoformat()
        d['status'] = str(self.status)
        return d


@dataclass
class ABTestResult:
    """A/B 测试结果"""
    experiment_id: str
    variant_name: str
    sample_size: int
    metrics: Dict[str, float]  # metric_name -> value
    confidence_level: float = 0.95

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class MetricData:
    """单个指标数据点"""
    user_id: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """转换为字典"""
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d


class ABTestingFramework:
    """A/B 测试框架"""

    def __init__(self, storage_dir: str = "data/ab_tests"):
        """
        初始化框架

        Args:
            storage_dir: 数据存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 实验缓存
        self.experiments: Dict[str, ABExperiment] = {}

        # 用户分配
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {experiment_id: variant}

        # 指标数据
        self.metrics_data: Dict[str, Dict[str, Dict[str, List[MetricData]]]] = {}
        # experiment_id -> {variant -> {metric_name -> [MetricData]}}

        # 统计缓存
        self.analysis_cache: Dict[str, Dict] = {}

        logger.info(f"A/B 测试框架已初始化，存储目录: {self.storage_dir}")

    def create_experiment(
        self,
        experiment_id: str,
        name: str,
        description: str,
        variants: Dict[str, Dict],
        traffic_split: Optional[Dict[str, float]] = None,
        metrics: Optional[List[str]] = None,
        tags: Optional[Dict[str, Any]] = None
    ) -> ABExperiment:
        """
        创建 A/B 测试实验

        Args:
            experiment_id: 实验ID
            name: 实验名称
            description: 实验描述
            variants: 变体配置 {variant_name: config_dict}
            traffic_split: 流量分配 {variant_name: percentage}
            metrics: 指标列表
            tags: 标签/元数据

        Returns:
            ABExperiment 对象
        """
        # 默认平均分配流量
        if traffic_split is None:
            n = len(variants)
            traffic_split = {v: 1.0/n for v in variants.keys()}
        else:
            # 验证流量分配总和
            total = sum(traffic_split.values())
            if not (0.99 < total < 1.01):
                raise ValueError(f"流量分配总和必须为 1.0，当前: {total}")

        # 默认指标
        if metrics is None:
            metrics = [
                'completion_rate',
                'user_rating',
                'watch_time',
                'engagement_score'
            ]

        # 默认标签
        if tags is None:
            tags = {}

        experiment = ABExperiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            variants=variants,
            traffic_split=traffic_split,
            metrics=metrics,
            status=ExperimentStatus.DRAFT,
            tags=tags
        )

        self.experiments[experiment_id] = experiment
        self.metrics_data[experiment_id] = {
            variant: {} for variant in variants.keys()
        }

        self._save_experiment(experiment)
        logger.info(f"创建实验: {experiment_id} ({name})")

        return experiment

    def start_experiment(self, experiment_id: str) -> ABExperiment:
        """启动实验"""
        if experiment_id not in self.experiments:
            raise ValueError(f"实验不存在: {experiment_id}")

        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.RUNNING
        experiment.start_time = datetime.now()

        self._save_experiment(experiment)
        logger.info(f"启动实验: {experiment_id}")

        return experiment

    def stop_experiment(self, experiment_id: str) -> ABExperiment:
        """停止实验"""
        if experiment_id not in self.experiments:
            raise ValueError(f"实验不存在: {experiment_id}")

        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED
        experiment.end_time = datetime.now()

        self._save_experiment(experiment)
        logger.info(f"停止实验: {experiment_id}")

        return experiment

    def pause_experiment(self, experiment_id: str) -> ABExperiment:
        """暂停实验"""
        if experiment_id not in self.experiments:
            raise ValueError(f"实验不存在: {experiment_id}")

        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.PAUSED

        self._save_experiment(experiment)
        logger.info(f"暂停实验: {experiment_id}")

        return experiment

    def assign_variant(
        self,
        user_id: str,
        experiment_id: str,
        seed: Optional[int] = None
    ) -> str:
        """
        为用户分配实验变体

        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            seed: 随机种子（用于可重现的分配）

        Returns:
            分配的变体名称
        """
        # 检查是否已分配
        if user_id in self.user_assignments:
            if experiment_id in self.user_assignments[user_id]:
                return self.user_assignments[user_id][experiment_id]

        # 获取实验
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"实验不存在: {experiment_id}")

        # 根据流量分配随机选择
        variants = list(experiment.traffic_split.keys())
        weights = list(experiment.traffic_split.values())

        if seed is not None:
            random.seed(seed)

        variant = random.choices(variants, weights=weights)[0]

        # 保存分配
        if user_id not in self.user_assignments:
            self.user_assignments[user_id] = {}
        self.user_assignments[user_id][experiment_id] = variant

        logger.debug(f"用户 {user_id} 分配到 {variant}")

        return variant

    def record_metric(
        self,
        user_id: str,
        experiment_id: str,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        记录指标数据

        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            metric_name: 指标名称
            value: 指标值
            metadata: 元数据

        Returns:
            是否成功记录
        """
        # 获取用户的变体
        variant = self.user_assignments.get(user_id, {}).get(experiment_id)
        if not variant:
            logger.warning(f"用户 {user_id} 未在实验 {experiment_id} 中分配")
            return False

        # 初始化数据结构
        if experiment_id not in self.metrics_data:
            self.metrics_data[experiment_id] = {}
        if variant not in self.metrics_data[experiment_id]:
            self.metrics_data[experiment_id][variant] = {}
        if metric_name not in self.metrics_data[experiment_id][variant]:
            self.metrics_data[experiment_id][variant][metric_name] = []

        # 创建指标数据
        metric_data = MetricData(
            user_id=user_id,
            value=value,
            metadata=metadata or {}
        )

        # 保存指标
        self.metrics_data[experiment_id][variant][metric_name].append(metric_data)

        # 清除分析缓存
        cache_key = f"{experiment_id}:{metric_name}"
        if cache_key in self.analysis_cache:
            del self.analysis_cache[cache_key]

        return True

    def analyze_experiment(
        self,
        experiment_id: str,
        metric_name: str,
        control_variant: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        分析实验结果

        Args:
            experiment_id: 实验ID
            metric_name: 指标名称
            control_variant: 对照组变体
            use_cache: 是否使用缓存

        Returns:
            分析结果字典
        """
        cache_key = f"{experiment_id}:{metric_name}"

        if use_cache and cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]

        if experiment_id not in self.metrics_data:
            return {'error': '没有数据'}

        data = self.metrics_data[experiment_id]

        # 提取各变体的数据
        results = {}

        for variant, metrics in data.items():
            if metric_name not in metrics:
                continue

            values = [m.value for m in metrics[metric_name]]

            if not values:
                continue

            results[variant] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values)),
                'count': len(values),
                'values': values
            }

        # 计算统计显著性
        if control_variant in results:
            control_values = np.array(results[control_variant]['values'])

            for variant in results:
                if variant == control_variant:
                    continue

                variant_values = np.array(results[variant]['values'])

                # 相对提升
                if results[control_variant]['mean'] != 0:
                    improvement = (
                        (results[variant]['mean'] - results[control_variant]['mean']) /
                        abs(results[control_variant]['mean']) * 100
                    )
                else:
                    improvement = 0
                results[variant]['improvement'] = float(improvement)

                # t-test
                if SCIPY_AVAILABLE and len(control_values) > 1 and len(variant_values) > 1:
                    t_stat, p_value = stats.ttest_ind(control_values, variant_values)

                    results[variant]['t_statistic'] = float(t_stat)
                    results[variant]['p_value'] = float(p_value)
                    results[variant]['significant'] = bool(p_value < 0.05)

                    # 95% 置信区间
                    se = np.sqrt(
                        results[control_variant]['std']**2 / len(control_values) +
                        results[variant]['std']**2 / len(variant_values)
                    )
                    ci = 1.96 * se
                    results[variant]['confidence_interval'] = float(ci)

        analysis_result = {
            'experiment_id': experiment_id,
            'metric': metric_name,
            'control': control_variant,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }

        if use_cache:
            self.analysis_cache[cache_key] = analysis_result

        return analysis_result

    def compare_variants(
        self,
        experiment_id: str,
        metric_name: str,
        variants: List[str]
    ) -> Dict[str, Any]:
        """
        对比多个变体

        Args:
            experiment_id: 实验ID
            metric_name: 指标名称
            variants: 变体列表

        Returns:
            对比结果
        """
        if experiment_id not in self.metrics_data:
            return {'error': '没有数据'}

        data = self.metrics_data[experiment_id]
        results = {}

        for variant in variants:
            if variant not in data or metric_name not in data[variant]:
                continue

            values = [m.value for m in data[variant][metric_name]]
            if not values:
                continue

            results[variant] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'count': len(values)
            }

        # 计算方差分析（ANOVA）
        if len(results) > 2 and SCIPY_AVAILABLE:
            value_lists = []
            for variant in variants:
                if variant in data and metric_name in data[variant]:
                    values = [m.value for m in data[variant][metric_name]]
                    if values:
                        value_lists.append(np.array(values))

            if len(value_lists) > 1:
                f_stat, p_value = stats.f_oneway(*value_lists)
                results['anova'] = {
                    'f_statistic': float(f_stat),
                    'p_value': float(p_value),
                    'significant': bool(p_value < 0.05)
                }

        return {
            'experiment_id': experiment_id,
            'metric': metric_name,
            'results': results
        }

    def generate_report(
        self,
        experiment_id: str,
        control_variant: str
    ) -> str:
        """
        生成测试报告

        Args:
            experiment_id: 实验ID
            control_variant: 对照组变体

        Returns:
            报告文本
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return "实验不存在"

        report = []
        report.append("=" * 70)
        report.append(f"A/B 测试报告: {experiment.name}")
        report.append("=" * 70)

        report.append(f"\n## 实验信息")
        report.append(f"ID: {experiment_id}")
        report.append(f"描述: {experiment.description}")
        report.append(f"状态: {experiment.status}")
        report.append(f"变体: {', '.join(experiment.variants.keys())}")
        report.append(f"流量分配: {', '.join(f'{v}({p:.1%})' for v, p in experiment.traffic_split.items())}")

        if experiment.start_time:
            report.append(f"开始时间: {experiment.start_time.isoformat()}")
        if experiment.end_time:
            report.append(f"结束时间: {experiment.end_time.isoformat()}")

        report.append(f"\n## 结果分析")

        for metric in experiment.metrics:
            analysis = self.analyze_experiment(
                experiment_id,
                metric,
                control_variant
            )

            if 'error' in analysis:
                continue

            report.append(f"\n### {metric}")

            for variant, result in analysis['results'].items():
                report.append(f"\n  **{variant}**:")
                report.append(f"    样本量: {result['count']}")
                report.append(f"    平均值: {result['mean']:.4f}")
                report.append(f"    标准差: {result['std']:.4f}")
                report.append(f"    最小值: {result['min']:.4f}")
                report.append(f"    最大值: {result['max']:.4f}")
                report.append(f"    中位数: {result['median']:.4f}")

                if variant != control_variant:
                    improvement = result.get('improvement', 0)
                    p_value = result.get('p_value', 1)
                    is_sig = result.get('significant', False)
                    ci = result.get('confidence_interval', 0)

                    report.append(f"    相对提升: {improvement:+.2f}%")
                    report.append(f"    P-value: {p_value:.6f}")
                    report.append(f"    统计显著: {'✓ 是' if is_sig else '✗ 否'}")
                    report.append(f"    95% 置信区间: ±{ci:.4f}")

        report.append(f"\n{'=' * 70}")
        report.append(f"生成时间: {datetime.now().isoformat()}")
        report.append(f"{'=' * 70}")

        return '\n'.join(report)

    def export_data(
        self,
        experiment_id: str,
        output_format: str = "json"
    ) -> str:
        """
        导出实验数据

        Args:
            experiment_id: 实验ID
            output_format: 输出格式 ('json' 或 'csv')

        Returns:
            导出的数据
        """
        if experiment_id not in self.metrics_data:
            return ""

        if output_format == "json":
            data = {
                'experiment_id': experiment_id,
                'timestamp': datetime.now().isoformat(),
                'metrics_data': {}
            }

            for variant, metrics in self.metrics_data[experiment_id].items():
                data['metrics_data'][variant] = {}
                for metric_name, metric_list in metrics.items():
                    data['metrics_data'][variant][metric_name] = [
                        m.to_dict() for m in metric_list
                    ]

            return json.dumps(data, ensure_ascii=False, indent=2)

        elif output_format == "csv":
            import csv
            from io import StringIO

            output = StringIO()
            writer = csv.writer(output)

            # 写入头部
            writer.writerow(['variant', 'metric', 'user_id', 'value', 'timestamp'])

            # 写入数据
            for variant, metrics in self.metrics_data[experiment_id].items():
                for metric_name, metric_list in metrics.items():
                    for m in metric_list:
                        writer.writerow([
                            variant,
                            metric_name,
                            m.user_id,
                            m.value,
                            m.timestamp.isoformat()
                        ])

            return output.getvalue()

        return ""

    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """获取实验总结"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return {}

        summary = {
            'experiment_id': experiment_id,
            'name': experiment.name,
            'status': experiment.status,
            'variants': list(experiment.variants.keys()),
            'total_users': len([
                u for u in self.user_assignments
                if experiment_id in self.user_assignments[u]
            ]),
            'metrics': {}
        }

        # 统计各变体的用户数
        variant_counts = {}
        for user_id, assignments in self.user_assignments.items():
            if experiment_id in assignments:
                variant = assignments[experiment_id]
                variant_counts[variant] = variant_counts.get(variant, 0) + 1

        summary['variant_distribution'] = variant_counts

        # 统计各指标的数据点
        for metric in experiment.metrics:
            metric_count = 0
            if experiment_id in self.metrics_data:
                for variant_metrics in self.metrics_data[experiment_id].values():
                    if metric in variant_metrics:
                        metric_count += len(variant_metrics[metric])
            summary['metrics'][metric] = metric_count

        return summary

    def _save_experiment(self, experiment: ABExperiment):
        """保存实验配置"""
        filepath = self.storage_dir / f"{experiment.experiment_id}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(experiment.to_dict(), f, ensure_ascii=False, indent=2)

    def load_experiment(self, experiment_id: str) -> Optional[ABExperiment]:
        """加载实验配置"""
        filepath = self.storage_dir / f"{experiment_id}.json"

        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 转换日期时间
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])

        experiment = ABExperiment(**data)
        self.experiments[experiment_id] = experiment

        return experiment

    def list_experiments(self) -> List[str]:
        """列出所有实验ID"""
        return list(self.experiments.keys())

    def get_experiment(self, experiment_id: str) -> Optional[ABExperiment]:
        """获取实验对象"""
        return self.experiments.get(experiment_id)


class VideoEditorABTesting:
    """视频编辑器 A/B 测试集成"""

    def __init__(self, ab_framework: ABTestingFramework):
        """
        初始化集成

        Args:
            ab_framework: ABTestingFramework 实例
        """
        self.ab_framework = ab_framework
        self.current_experiment_id: Optional[str] = None
        self.current_user_id: Optional[str] = None
        self.current_variant: Optional[str] = None

    def set_experiment(self, experiment_id: str, user_id: str) -> str:
        """
        设置当前实验和用户

        Args:
            experiment_id: 实验ID
            user_id: 用户ID

        Returns:
            分配的变体
        """
        self.current_experiment_id = experiment_id
        self.current_user_id = user_id

        # 为用户分配变体
        variant = self.ab_framework.assign_variant(user_id, experiment_id)
        self.current_variant = variant

        return variant

    def record_metric(
        self,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """记录指标"""
        if not self.current_experiment_id or not self.current_user_id:
            return False

        return self.ab_framework.record_metric(
            self.current_user_id,
            self.current_experiment_id,
            metric_name,
            value,
            metadata
        )

    def get_variant_config(self) -> Optional[Dict]:
        """获取当前变体配置"""
        if not self.current_experiment_id or not self.current_variant:
            return None

        experiment = self.ab_framework.get_experiment(self.current_experiment_id)
        if not experiment:
            return None

        return experiment.variants.get(self.current_variant)


if __name__ == "__main__":
    # 示例用法
    logging.basicConfig(level=logging.INFO)

    print("A/B 测试框架已加载")
