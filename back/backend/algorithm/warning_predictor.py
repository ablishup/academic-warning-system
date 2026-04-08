"""
预警预测器 - 基于随机森林

使用随机森林算法预测学生学业风险等级
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
import joblib
import os
import logging

from django.conf import settings

from .features import FeatureExtractor, FeatureEngineering

logger = logging.getLogger(__name__)


class WarningPredictor:
    """
    学业预警预测器

    使用随机森林模型进行风险等级预测
    """

    # 模型文件路径
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'algorithm', 'models')

    def __init__(self):
        self.classifier = None  # 分类器（预测风险等级）
        self.regressor = None   # 回归器（预测具体得分）
        self.is_trained = False
        self._ensure_model_dir()

    def _ensure_model_dir(self):
        """确保模型目录存在"""
        if not os.path.exists(self.MODEL_PATH):
            os.makedirs(self.MODEL_PATH)

    def train(self, training_data=None):
        """
        训练随机森林模型

        Args:
            training_data: 训练数据，格式为 [(features_dict, score, risk_level), ...]
                          如果为None，则使用模拟数据训练

        Returns:
            dict: 训练结果
        """
        if training_data is None:
            # 使用模拟数据训练（实际应用中应使用历史数据）
            training_data = self._generate_training_data()

        # 准备特征和标签
        X = []
        y_score = []      # 回归目标：具体得分
        y_risk_level = [] # 分类目标：风险等级

        feature_names = FeatureEngineering.get_feature_names()

        for features_dict, score, risk_level in training_data:
            feature_vector = [features_dict.get(f, 0) for f in feature_names]
            X.append(feature_vector)
            y_score.append(score)
            y_risk_level.append(risk_level)

        X = np.array(X)
        y_score = np.array(y_score)
        y_risk_level = np.array(y_risk_level)

        # 划分训练集和测试集
        if len(X) >= 10:  # 数据足够时划分
            X_train, X_test, y_score_train, y_score_test, y_level_train, y_level_test = train_test_split(
                X, y_score, y_risk_level, test_size=0.2, random_state=42
            )
        else:
            X_train, X_test = X, X
            y_score_train, y_score_test = y_score, y_score
            y_level_train, y_level_test = y_risk_level, y_risk_level

        # 训练分类器（预测风险等级）
        self.classifier = RandomForestClassifier(
            n_estimators=100,      # 树的数量
            max_depth=10,          # 最大深度
            min_samples_split=5,   # 内部节点再划分所需最小样本数
            min_samples_leaf=2,    # 叶子节点最小样本数
            random_state=42,
            n_jobs=-1              # 使用所有CPU核心
        )
        self.classifier.fit(X_train, y_level_train)

        # 训练回归器（预测具体得分）
        self.regressor = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.regressor.fit(X_train, y_score_train)

        self.is_trained = True

        # 评估模型
        results = self._evaluate_model(
            X_test, y_score_test, y_level_test
        )

        # 保存模型
        self._save_model()

        return results

    def predict(self, student_id=None, course_id=None, features_dict=None):
        """
        预测学生风险等级

        Args:
            student_id: 学生ID
            course_id: 课程ID（可选）
            features_dict: 预计算的特征字典（如果提供则跳过特征提取）

        Returns:
            dict: 预测结果
        """
        if not self.is_trained:
            # 如果模型未训练，使用传统加权方法
            return self._weighted_prediction(student_id, course_id, features_dict)

        # 提取特征
        if features_dict is None:
            extractor = FeatureExtractor(student_id, course_id)
            features_dict = extractor.extract_features()

        # 构建特征向量
        feature_names = FeatureEngineering.get_feature_names()
        X = np.array([[features_dict.get(f, 0) for f in feature_names]])

        # 预测
        risk_level = self.classifier.predict(X)[0]
        risk_proba = self.classifier.predict_proba(X)[0]
        predicted_score = self.regressor.predict(X)[0]

        # 获取特征重要性
        feature_importance = dict(zip(
            feature_names,
            self.classifier.feature_importances_
        ))

        # 排序特征重要性
        feature_importance = dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))

        return {
            'risk_level': risk_level,
            'predicted_score': round(predicted_score, 2),
            'risk_probability': dict(zip(
                self.classifier.classes_,
                [round(p * 100, 2) for p in risk_proba]
            )),
            'feature_importance': feature_importance,
            'features_used': features_dict,
            'model_type': 'random_forest'
        }

    def _weighted_prediction(self, student_id=None, course_id=None, features_dict=None):
        """
        使用传统加权方法预测（当模型未训练时）
        """
        if features_dict is None:
            extractor = FeatureExtractor(student_id, course_id)
            features_dict = extractor.extract_features()

        # 计算综合得分
        composite_score = FeatureEngineering.calculate_composite_score(features_dict)

        # 确定风险等级
        risk_level = FeatureEngineering.determine_risk_level(composite_score)

        return {
            'risk_level': risk_level,
            'predicted_score': composite_score,
            'risk_probability': {
                'high': 100 if risk_level == 'high' else 0,
                'medium': 100 if risk_level == 'medium' else 0,
                'low': 100 if risk_level == 'low' else 0,
                'normal': 100 if risk_level == 'normal' else 0,
            },
            'feature_importance': {},
            'features_used': features_dict,
            'model_type': 'weighted',
            'note': '使用加权计算（随机森林模型未训练）'
        }

    def _evaluate_model(self, X_test, y_score_test, y_level_test):
        """评估模型性能"""
        # 分类评估
        y_level_pred = self.classifier.predict(X_test)
        classification_metrics = classification_report(
            y_level_test, y_level_pred,
            output_dict=True
        )

        # 回归评估
        y_score_pred = self.regressor.predict(X_test)
        mse = mean_squared_error(y_score_test, y_score_pred)
        rmse = np.sqrt(mse)

        return {
            'classification_accuracy': classification_metrics.get('accuracy', 0),
            'classification_report': classification_metrics,
            'regression_rmse': round(rmse, 2),
            'feature_importance': dict(zip(
                FeatureEngineering.get_feature_names(),
                self.classifier.feature_importances_.tolist()
            ))
        }

    def _save_model(self):
        """保存模型到文件"""
        try:
            joblib.dump({
                'classifier': self.classifier,
                'regressor': self.regressor,
                'feature_names': FeatureEngineering.get_feature_names()
            }, os.path.join(self.MODEL_PATH, 'warning_model.pkl'))
            logger.info("模型保存成功")
        except Exception as e:
            logger.error(f"模型保存失败: {e}")

    def load_model(self):
        """从文件加载模型"""
        model_file = os.path.join(self.MODEL_PATH, 'warning_model.pkl')
        if os.path.exists(model_file):
            try:
                data = joblib.load(model_file)
                self.classifier = data['classifier']
                self.regressor = data['regressor']
                self.is_trained = True
                logger.info("模型加载成功")
                return True
            except Exception as e:
                logger.error(f"模型加载失败: {e}")
        return False

    def _generate_training_data(self, n_samples=200):
        """
        生成训练数据（模拟数据）

        在实际应用中，应该使用历史学生数据来训练模型
        """
        np.random.seed(42)
        training_data = []

        for _ in range(n_samples):
            # 生成随机特征
            attendance_rate = np.random.uniform(0, 100)
            video_progress = np.random.uniform(0, 100)
            homework_avg = np.random.uniform(0, 100)
            exam_avg = np.random.uniform(0, 100)

            features_dict = {
                'attendance_rate': attendance_rate,
                'video_progress': video_progress,
                'video_completion_rate': video_progress * np.random.uniform(0.8, 1.0),
                'homework_avg_score': homework_avg,
                'homework_submit_rate': np.random.uniform(60, 100),
                'homework_late_rate': np.random.uniform(0, 20),
                'exam_avg_score': exam_avg,
                'exam_pass_rate': 100 if exam_avg >= 60 else np.random.uniform(0, 50),
                'exam_attendance_rate': np.random.uniform(80, 100),
                'avg_daily_learning_minutes': np.random.uniform(10, 120),
            }

            # 计算综合得分
            composite = (
                attendance_rate * 0.3 +
                video_progress * 0.2 +
                homework_avg * 0.3 +
                exam_avg * 0.2
            )

            # 添加噪声
            composite += np.random.normal(0, 5)
            composite = np.clip(composite, 0, 100)

            # 确定风险等级
            risk_level = FeatureEngineering.determine_risk_level(composite)

            training_data.append((features_dict, composite, risk_level))

        return training_data

    def explain_prediction(self, features_dict):
        """
        解释预测结果

        分析哪些因素对预测结果影响最大
        """
        if not self.is_trained:
            return "模型未训练，无法提供解释"

        # 获取特征重要性
        feature_importance = dict(zip(
            FeatureEngineering.get_feature_names(),
            self.classifier.feature_importances_
        ))

        # 按重要性排序
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 找出主要问题
        issues = []
        for feature, importance in sorted_features[:3]:  # 前3个重要特征
            value = features_dict.get(feature, 0)
            if feature == 'attendance_rate' and value < 60:
                issues.append(f"出勤率较低 ({value:.1f}%)")
            elif feature == 'video_progress' and value < 60:
                issues.append(f"视频学习进度不足 ({value:.1f}%)")
            elif feature == 'homework_avg_score' and value < 60:
                issues.append(f"作业成绩偏低 ({value:.1f}分)")
            elif feature == 'exam_avg_score' and value < 60:
                issues.append(f"考试成绩不理想 ({value:.1f}分)")

        return {
            'top_features': sorted_features[:5],
            'identified_issues': issues,
            'suggestions': self._generate_suggestions(issues)
        }

    def _generate_suggestions(self, issues):
        """生成改进建议"""
        suggestions = []
        for issue in issues:
            if '出勤' in issue:
                suggestions.append("建议加强考勤管理，按时参加课程学习")
            elif '视频' in issue:
                suggestions.append("建议增加在线学习时间，及时完成视频课程")
            elif '作业' in issue:
                suggestions.append("建议认真对待作业，遇到问题及时向老师请教")
            elif '考试' in issue:
                suggestions.append("建议加强复习，做好考前准备")

        return suggestions
