"""
算法API视图

提供随机森林模型训练、预测、解释等接口
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .warning_predictor import WarningPredictor
from .features import FeatureExtractor, FeatureEngineering


class TrainModelView(APIView):
    """
    训练预警模型视图

    POST /api/algorithm/train/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        """训练随机森林模型"""
        predictor = WarningPredictor()

        # 获取训练数据（如果有）
        training_data = request.data.get('training_data', None)

        # 训练模型
        results = predictor.train(training_data)

        return Response({
            'code': 200,
            'message': '模型训练完成',
            'data': {
                'classification_accuracy': results['classification_accuracy'],
                'regression_rmse': results['regression_rmse'],
                'feature_importance': results['feature_importance']
            }
        })


class PredictWarningView(APIView):
    """
    预测学业风险视图

    POST /api/algorithm/predict/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """预测学生学业风险"""
        student_id = request.data.get('student_id')
        course_id = request.data.get('course_id', None)

        if not student_id:
            return Response({
                'code': 400,
                'message': '需要指定student_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        predictor = WarningPredictor()

        # 尝试加载已有模型
        if not predictor.load_model():
            # 如果没有已训练模型，使用模拟数据训练
            predictor.train()

        # 进行预测
        result = predictor.predict(student_id=student_id, course_id=course_id)

        # 获取预测解释
        features = result.get('features_used', {})
        explanation = predictor.explain_prediction(features)

        return Response({
            'code': 200,
            'message': '预测完成',
            'data': {
                'student_id': student_id,
                'course_id': course_id,
                'risk_level': result['risk_level'],
                'predicted_score': result['predicted_score'],
                'risk_probability': result['risk_probability'],
                'feature_importance': result['feature_importance'],
                'model_type': result.get('model_type', 'random_forest'),
                'explanation': explanation
            }
        })


class ExtractFeaturesView(APIView):
    """
    提取特征视图

    GET /api/algorithm/features/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """提取学生学习特征"""
        student_id = request.query_params.get('student_id')
        course_id = request.query_params.get('course_id')

        if not student_id:
            return Response({
                'code': 400,
                'message': '需要指定student_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        extractor = FeatureExtractor(
            student_id=int(student_id),
            course_id=int(course_id) if course_id else None
        )

        features = extractor.extract_features()

        # 计算综合得分
        composite_score = FeatureEngineering.calculate_composite_score(features)
        risk_level = FeatureEngineering.determine_risk_level(composite_score)

        return Response({
            'code': 200,
            'message': '特征提取完成',
            'data': {
                'student_id': student_id,
                'course_id': course_id,
                'features': features,
                'composite_score': composite_score,
                'risk_level': risk_level
            }
        })


class ModelStatusView(APIView):
    """
    模型状态视图

    GET /api/algorithm/status/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取模型状态"""
        predictor = WarningPredictor()
        is_loaded = predictor.load_model()

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'model_exists': is_loaded,
                'model_type': 'RandomForest',
                'features_count': len(FeatureEngineering.get_feature_names()),
                'feature_weights': FeatureEngineering.FEATURE_WEIGHTS
            }
        })


class FeatureImportanceView(APIView):
    """
    特征重要性视图

    GET /api/algorithm/feature-importance/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取特征重要性（需要先训练模型）"""
        predictor = WarningPredictor()

        if not predictor.load_model():
            return Response({
                'code': 404,
                'message': '模型未训练，请先训练模型'
            }, status=status.HTTP_404_NOT_FOUND)

        # 获取特征重要性
        importance = dict(zip(
            FeatureEngineering.get_feature_names(),
            predictor.classifier.feature_importances_.tolist()
        ))

        # 排序
        sorted_importance = sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'feature_importance': importance,
                'sorted_importance': sorted_importance
            }
        })
