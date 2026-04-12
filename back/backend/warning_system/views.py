from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import Student
from courses.models import Course
from algorithm.warning_predictor import WarningPredictor
from algorithm.features import FeatureEngineering

from .models import WarningRecord, StudentCourseScore
from .serializers import (
    WarningRecordListSerializer,
    WarningRecordDetailSerializer,
    WarningCalculateSerializer,
    WarningResolveSerializer,
    StudentCourseScoreSerializer,
    WarningStatsSerializer,
)
from .data_sync import DataSynchronizer


def get_student_from_user(user):
    """从当前登录用户获取学生ID"""
    if not user or not user.is_authenticated:
        return None

    # 方法1: 通过 username 匹配 name（学号）
    # 注意：数据库中 name 字段存的是学号，student_no 存的是姓名
    student = Student.objects.filter(name=user.username).first()
    if student:
        return student.id

    # 方法2: 通过 first_name 匹配 student_no（姓名）
    if user.first_name:
        student = Student.objects.filter(student_no=user.first_name).first()
        if student:
            return student.id

    # 方法3: 通过 username 匹配 student_no（兼容旧数据）
    student = Student.objects.filter(student_no=user.username).first()
    if student:
        return student.id

    # 方法4: 通过 username 解析 (如 student_1 -> id=1)
    if user.username.startswith('student_'):
        try:
            student_id = int(user.username.split('_')[1])
            student = Student.objects.filter(id=student_id).first()
            if student:
                return student.id
        except (ValueError, IndexError):
            pass

    # 方法5: 通过 profile 关联 (如果存在)
    try:
        profile = getattr(user, 'profile', None)
        if profile and hasattr(profile, 'employee_no') and profile.employee_no:
            student = Student.objects.filter(name=profile.employee_no).first()
            if student:
                return student.id
    except:
        pass

    return None


class WarningRecordListView(generics.ListAPIView):
    """预警列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = WarningRecordListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'student__student_no', 'course__name']
    ordering_fields = ['calculation_time', 'composite_score', 'created_at']
    ordering = ['-calculation_time']

    def get_queryset(self):
        queryset = WarningRecord.objects.all()

        # 筛选参数
        risk_level = self.request.query_params.get('risk_level')
        status = self.request.query_params.get('status')
        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')

        # 如果没有提供student_id，尝试从当前用户推断
        if not student_id:
            student_id = get_student_from_user(self.request.user)

        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        if status:
            queryset = queryset.filter(status=status)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.select_related('student', 'course')


class WarningRecordDetailView(generics.RetrieveAPIView):
    """预警详情视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = WarningRecordDetailSerializer
    queryset = WarningRecord.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        return WarningRecord.objects.select_related('student', 'course', 'resolved_by')


class WarningCalculateView(APIView):
    """计算预警视图 - 使用随机森林算法"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WarningCalculateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        student_id = serializer.validated_data.get('student_id')
        course_id = serializer.validated_data.get('course_id')

        # 获取需要计算的学生-课程组合
        scores_query = StudentCourseScore.objects.all()
        if student_id:
            scores_query = scores_query.filter(student_id=student_id)
        if course_id:
            scores_query = scores_query.filter(course_id=course_id)

        # 初始化预测器
        predictor = WarningPredictor()
        # 尝试加载已有模型，如果没有则使用传统方法
        use_ml = predictor.load_model()
        if not use_ml:
            # 尝试训练模型（使用默认数据）
            try:
                predictor.train()
                use_ml = True
            except Exception as e:
                # 训练失败则使用传统加权方法
                use_ml = False

        # 计算预警
        created_count = 0
        updated_count = 0
        calculation_results = []

        for score in scores_query.select_related('student', 'course'):
            # 构建特征字典
            features_dict = {
                'attendance_rate': float(score.attendance_rate or 0),
                'video_progress': float(score.video_progress or 0),
                'homework_avg_score': float(score.homework_avg or 0),
                'exam_avg_score': float(score.exam_avg or 0),
            }

            # 使用随机森林或加权方法预测
            if use_ml:
                prediction = predictor.predict(
                    student_id=score.student_id,
                    course_id=score.course_id,
                    features_dict=features_dict
                )
                composite_score = prediction['predicted_score']
                risk_level = prediction['risk_level']
            else:
                # 使用传统加权方法
                composite_score = FeatureEngineering.calculate_composite_score(features_dict)
                risk_level = FeatureEngineering.determine_risk_level(composite_score)

            # 检查是否已存在预警记录
            existing_warning = WarningRecord.objects.filter(
                student=score.student,
                course=score.course,
                status='active'
            ).first()

            if existing_warning:
                # 更新现有预警
                existing_warning.composite_score = composite_score
                existing_warning.risk_level = risk_level
                existing_warning.attendance_score = score.attendance_rate
                existing_warning.progress_score = score.video_progress
                existing_warning.homework_score = score.homework_avg
                existing_warning.exam_score = score.exam_avg
                existing_warning.calculation_time = timezone.now()
                existing_warning.save()
                updated_count += 1
                result = 'updated'
            else:
                # 创建新预警（只对非normal等级）
                result = 'no_change'
                if risk_level != 'normal':
                    WarningRecord.objects.create(
                        student=score.student,
                        course=score.course,
                        risk_level=risk_level,
                        composite_score=composite_score,
                        attendance_score=score.attendance_rate,
                        progress_score=score.video_progress,
                        homework_score=score.homework_avg,
                        exam_score=score.exam_avg,
                    )
                    created_count += 1
                    result = 'created'

            calculation_results.append({
                'student_id': score.student_id,
                'student_name': score.student.name,
                'course_id': score.course_id,
                'course_name': score.course.name if score.course else None,
                'composite_score': composite_score,
                'risk_level': risk_level,
                'result': result
            })

        return Response({
            'code': 200,
            'message': '预警计算完成',
            'data': {
                'created': created_count,
                'updated': updated_count,
                'model_used': 'random_forest' if use_ml else 'weighted',
                'results': calculation_results[:10] if student_id else None  # 单学生时返回详情
            }
        })


class WarningResolveView(APIView):
    """解决预警视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            warning = WarningRecord.objects.get(pk=pk)
        except WarningRecord.DoesNotExist:
            return Response({
                'code': 404,
                'message': '预警记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = WarningResolveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        warning.status = 'resolved'
        warning.resolved_at = timezone.now()
        warning.resolved_by = request.user
        warning.resolve_note = serializer.validated_data.get('resolve_note', '')
        warning.save()

        return Response({
            'code': 200,
            'message': '预警已解决',
            'data': {
                'id': warning.id,
                'status': warning.status,
                'resolved_at': warning.resolved_at,
            }
        })


class WarningStatsView(APIView):
    """预警统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = WarningRecord.objects.aggregate(
            total_warnings=Count('id'),
            high_risk_count=Count('id', filter=Q(risk_level='high')),
            medium_risk_count=Count('id', filter=Q(risk_level='medium')),
            low_risk_count=Count('id', filter=Q(risk_level='low')),
            normal_count=Count('id', filter=Q(risk_level='normal')),
            active_count=Count('id', filter=Q(status='active')),
            resolved_count=Count('id', filter=Q(status='resolved')),
        )

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': stats
        })


class StudentCourseScoreListView(generics.ListAPIView):
    """学生课程综合得分列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = StudentCourseScoreSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['last_calculated', 'final_score']
    ordering = ['-last_calculated']

    def get_queryset(self):
        queryset = StudentCourseScore.objects.all()

        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')

        # 如果没有提供student_id，尝试从当前用户推断
        if not student_id:
            student_id = get_student_from_user(self.request.user)

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.select_related('student', 'course')


class SyncStudentScoresView(APIView):
    """同步学生课程得分视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """触发数据同步"""
        try:
            # 获取参数
            student_id = request.data.get('student_id')
            course_id = request.data.get('course_id')
            sync_all = request.data.get('sync_all', False)

            if sync_all:
                # 同步所有学生
                results = DataSynchronizer.sync_all_students_scores()
                success_count = sum(1 for r in results if r['status'] == 'success')

                return Response({
                    'code': 200,
                    'message': '数据同步完成',
                    'data': {
                        'total': len(results),
                        'success': success_count,
                        'failed': len(results) - success_count
                    }
                })
            elif student_id and course_id:
                # 同步单个学生
                score = DataSynchronizer.calculate_student_course_score(
                    student_id, course_id
                )
                return Response({
                    'code': 200,
                    'message': '同步成功',
                    'data': {
                        'student_id': student_id,
                        'course_id': course_id,
                        'attendance_rate': score.attendance_rate,
                        'video_progress': score.video_progress,
                        'homework_avg': score.homework_avg,
                        'exam_avg': score.exam_avg,
                    }
                })
            else:
                return Response({
                    'code': 400,
                    'message': '参数错误：请提供 student_id 和 course_id，或设置 sync_all=true'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'同步失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SyncStatusView(APIView):
    """获取数据同步状态视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取同步统计信息"""
        stats = DataSynchronizer.get_sync_statistics()

        # 获取最近同步的得分记录
        recent_scores = StudentCourseScore.objects.select_related(
            'student', 'course'
        ).order_by('-last_calculated')[:5]

        recent_list = []
        for score in recent_scores:
            recent_list.append({
                'student_name': score.student.name if score.student else None,
                'student_no': score.student.student_no if score.student else None,
                'course_name': score.course.name if score.course else None,
                'final_score': score.final_score,
                'last_calculated': score.last_calculated
            })

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'statistics': stats,
                'recent_synced': recent_list
            }
        })
