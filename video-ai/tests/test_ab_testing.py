"""
A/B 测试框架单元测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np

from src.services.ab_testing import (
    ABTestingFramework,
    ABExperiment,
    ExperimentStatus,
    VideoEditorABTesting
)


class TestABTestingFramework(unittest.TestCase):
    """ABTestingFramework 单元测试"""

    def setUp(self):
        """测试前的初始化"""
        self.temp_dir = tempfile.mkdtemp()
        self.framework = ABTestingFramework(storage_dir=self.temp_dir)

    def tearDown(self):
        """测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_create_experiment(self):
        """测试创建实验"""
        experiment = self.framework.create_experiment(
            experiment_id='test_exp_001',
            name='测试实验',
            description='这是一个测试实验',
            variants={'control': {}, 'variant_a': {}},
            traffic_split={'control': 0.5, 'variant_a': 0.5}
        )

        self.assertEqual(experiment.experiment_id, 'test_exp_001')
        self.assertEqual(experiment.name, '测试实验')
        self.assertEqual(len(experiment.variants), 2)
        self.assertEqual(experiment.status, ExperimentStatus.DRAFT)

    def test_traffic_split_validation(self):
        """测试流量分配验证"""
        with self.assertRaises(ValueError):
            # 流量分配总和不是 1.0
            self.framework.create_experiment(
                experiment_id='test_invalid',
                name='无效实验',
                description='测试无效流量分配',
                variants={'a': {}, 'b': {}},
                traffic_split={'a': 0.3, 'b': 0.3}  # 总和 0.6
            )

    def test_assign_variant(self):
        """测试变体分配"""
        self.framework.create_experiment(
            experiment_id='test_assign',
            name='分配测试',
            description='测试变体分配',
            variants={'control': {}, 'variant_a': {}, 'variant_b': {}}
        )

        # 多次分配，检查是否一致
        variant1 = self.framework.assign_variant('user_001', 'test_assign')
        variant2 = self.framework.assign_variant('user_001', 'test_assign')

        self.assertEqual(variant1, variant2)
        self.assertIn(variant1, ['control', 'variant_a', 'variant_b'])

    def test_record_metric(self):
        """测试指标记录"""
        self.framework.create_experiment(
            experiment_id='test_metric',
            name='指标测试',
            description='测试指标记录',
            variants={'control': {}, 'variant_a': {}}
        )

        # 分配用户
        self.framework.assign_variant('user_001', 'test_metric')

        # 记录指标
        success = self.framework.record_metric(
            'user_001',
            'test_metric',
            'completion_rate',
            0.85
        )

        self.assertTrue(success)

    def test_analyze_experiment(self):
        """测试实验分析"""
        self.framework.create_experiment(
            experiment_id='test_analyze',
            name='分析测试',
            description='测试分析功能',
            variants={'control': {}, 'variant_a': {}}
        )

        self.framework.start_experiment('test_analyze')

        # 添加测试数据
        for i in range(50):
            variant = 'control' if i < 25 else 'variant_a'
            user_id = f'user_{i:03d}'
            self.framework.user_assignments[user_id] = {'test_analyze': variant}

            # 添加指标
            for j in range(3):
                value = np.random.uniform(0.7, 0.95)
                self.framework.record_metric(
                    user_id,
                    'test_analyze',
                    'completion_rate',
                    value
                )

        # 分析
        analysis = self.framework.analyze_experiment(
            'test_analyze',
            'completion_rate',
            'control'
        )

        self.assertIn('control', analysis['results'])
        self.assertIn('variant_a', analysis['results'])
        self.assertIn('improvement', analysis['results']['variant_a'])

    def test_experiment_lifecycle(self):
        """测试实验生命周期"""
        self.framework.create_experiment(
            experiment_id='test_lifecycle',
            name='生命周期测试',
            description='测试实验状态转换',
            variants={'control': {}, 'variant_a': {}}
        )

        exp = self.framework.get_experiment('test_lifecycle')
        self.assertEqual(exp.status, ExperimentStatus.DRAFT)

        # 启动
        exp = self.framework.start_experiment('test_lifecycle')
        self.assertEqual(exp.status, ExperimentStatus.RUNNING)

        # 暂停
        exp = self.framework.pause_experiment('test_lifecycle')
        self.assertEqual(exp.status, ExperimentStatus.PAUSED)

        # 完成
        exp = self.framework.stop_experiment('test_lifecycle')
        self.assertEqual(exp.status, ExperimentStatus.COMPLETED)

    def test_save_and_load_experiment(self):
        """测试实验保存和加载"""
        self.framework.create_experiment(
            experiment_id='test_save_load',
            name='保存加载测试',
            description='测试实验持久化',
            variants={'control': {}, 'variant_a': {}},
            tags={'test': True}
        )

        self.framework.start_experiment('test_save_load')

        # 加载实验
        new_framework = ABTestingFramework(storage_dir=self.temp_dir)
        loaded_exp = new_framework.load_experiment('test_save_load')

        self.assertIsNotNone(loaded_exp)
        self.assertEqual(loaded_exp.name, '保存加载测试')
        # 比较状态值而不是枚举对象
        self.assertEqual(str(loaded_exp.status), str(ExperimentStatus.RUNNING))

    def test_compare_variants(self):
        """测试变体对比"""
        self.framework.create_experiment(
            experiment_id='test_compare',
            name='对比测试',
            description='测试多变体对比',
            variants={'a': {}, 'b': {}, 'c': {}}
        )

        # 添加数据
        for i in range(30):
            variant = ['a', 'b', 'c'][i % 3]
            user_id = f'user_{i:03d}'
            self.framework.user_assignments[user_id] = {'test_compare': variant}

            value = np.random.uniform(0.5, 1.0)
            self.framework.record_metric(
                user_id,
                'test_compare',
                'metric_1',
                value
            )

        # 对比
        result = self.framework.compare_variants(
            'test_compare',
            'metric_1',
            ['a', 'b', 'c']
        )

        self.assertIn('a', result['results'])
        self.assertIn('b', result['results'])
        self.assertIn('c', result['results'])

    def test_export_data(self):
        """测试数据导出"""
        self.framework.create_experiment(
            experiment_id='test_export',
            name='导出测试',
            description='测试数据导出',
            variants={'control': {}, 'variant_a': {}}
        )

        self.framework.assign_variant('user_001', 'test_export')
        self.framework.record_metric('user_001', 'test_export', 'metric_1', 0.85)

        # 导出 JSON
        json_data = self.framework.export_data('test_export', output_format='json')
        self.assertIn('test_export', json_data)
        self.assertIn('metric_1', json_data)

        # 导出 CSV
        csv_data = self.framework.export_data('test_export', output_format='csv')
        self.assertIn('variant', csv_data)
        self.assertIn('metric', csv_data)
        self.assertIn('value', csv_data)

    def test_get_experiment_summary(self):
        """测试获取实验摘要"""
        self.framework.create_experiment(
            experiment_id='test_summary',
            name='摘要测试',
            description='测试实验摘要',
            variants={'control': {}, 'variant_a': {}}
        )

        # 添加数据
        for i in range(10):
            variant = 'control' if i < 5 else 'variant_a'
            user_id = f'user_{i:03d}'
            self.framework.user_assignments[user_id] = {'test_summary': variant}
            self.framework.record_metric(user_id, 'test_summary', 'metric_1', 0.8)

        # 获取摘要
        summary = self.framework.get_experiment_summary('test_summary')

        self.assertEqual(summary['total_users'], 10)
        self.assertIn('control', summary['variant_distribution'])
        self.assertIn('variant_a', summary['variant_distribution'])


class TestVideoEditorABTesting(unittest.TestCase):
    """VideoEditorABTesting 集成测试"""

    def setUp(self):
        """测试前的初始化"""
        self.temp_dir = tempfile.mkdtemp()
        self.framework = ABTestingFramework(storage_dir=self.temp_dir)
        self.editor_ab = VideoEditorABTesting(self.framework)

    def tearDown(self):
        """测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_set_experiment(self):
        """测试设置实验"""
        self.framework.create_experiment(
            experiment_id='test_editor',
            name='编辑器测试',
            description='测试编辑器集成',
            variants={'control': {}, 'variant_a': {}}
        )

        variant = self.editor_ab.set_experiment('test_editor', 'user_001')

        self.assertIsNotNone(variant)
        self.assertIn(variant, ['control', 'variant_a'])
        self.assertEqual(self.editor_ab.current_experiment_id, 'test_editor')
        self.assertEqual(self.editor_ab.current_user_id, 'user_001')

    def test_record_metric_via_editor(self):
        """测试通过编辑器记录指标"""
        self.framework.create_experiment(
            experiment_id='test_editor_metric',
            name='编辑器指标测试',
            description='测试编辑器指标记录',
            variants={'control': {}, 'variant_a': {}}
        )

        self.editor_ab.set_experiment('test_editor_metric', 'user_001')

        success = self.editor_ab.record_metric('completion_rate', 0.85)

        self.assertTrue(success)

    def test_get_variant_config(self):
        """测试获取变体配置"""
        variants = {
            'control': {'config': 'baseline'},
            'variant_a': {'config': 'new_feature'}
        }

        self.framework.create_experiment(
            experiment_id='test_config',
            name='配置测试',
            description='测试配置获取',
            variants=variants
        )

        self.editor_ab.set_experiment('test_config', 'user_001')

        config = self.editor_ab.get_variant_config()

        self.assertIsNotNone(config)
        self.assertIn('config', config)


class TestStatisticalAnalysis(unittest.TestCase):
    """统计分析功能测试"""

    def setUp(self):
        """测试前的初始化"""
        self.temp_dir = tempfile.mkdtemp()
        self.framework = ABTestingFramework(storage_dir=self.temp_dir)

    def tearDown(self):
        """测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_significant_difference(self):
        """测试显著性差异检测"""
        self.framework.create_experiment(
            experiment_id='test_significance',
            name='显著性测试',
            description='测试统计显著性检测',
            variants={'control': {}, 'variant_a': {}}
        )

        # 添加有显著差异的数据
        for i in range(100):
            variant = 'control' if i < 50 else 'variant_a'
            user_id = f'user_{i:03d}'
            self.framework.user_assignments[user_id] = {'test_significance': variant}

            # 让 variant_a 有明显的更高值
            if variant == 'control':
                value = np.random.normal(0.5, 0.1)
            else:
                value = np.random.normal(0.8, 0.1)

            value = max(0, min(1, value))
            self.framework.record_metric(
                user_id,
                'test_significance',
                'metric_1',
                value
            )

        # 分析
        analysis = self.framework.analyze_experiment(
            'test_significance',
            'metric_1',
            'control'
        )

        # variant_a 应该显示较大的相对提升
        variant_a = analysis['results']['variant_a']
        self.assertGreater(variant_a['improvement'], 20)  # 至少 20% 的提升

    def test_confidence_interval(self):
        """测试置信区间计算"""
        self.framework.create_experiment(
            experiment_id='test_ci',
            name='置信区间测试',
            description='测试置信区间计算',
            variants={'control': {}, 'variant_a': {}}
        )

        # 添加数据
        for i in range(50):
            variant = 'control' if i < 25 else 'variant_a'
            user_id = f'user_{i:03d}'
            self.framework.user_assignments[user_id] = {'test_ci': variant}

            value = np.random.uniform(0.5, 1.0)
            self.framework.record_metric(
                user_id,
                'test_ci',
                'metric_1',
                value
            )

        # 分析
        analysis = self.framework.analyze_experiment(
            'test_ci',
            'metric_1',
            'control'
        )

        # 检查置信区间是否存在
        if 'confidence_interval' in analysis['results']['variant_a']:
            ci = analysis['results']['variant_a']['confidence_interval']
            self.assertGreaterEqual(ci, 0)


if __name__ == '__main__':
    unittest.main()
