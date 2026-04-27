from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import Student
from users.utils import get_student_from_user
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


    # 方法1: 通过 username 匹配 student_no（学号）
    student = Student.objects.filter(student_no=user.username).first()
    if student:
        return student.id

    # 方法2: 通过 first_name 匹配 name（姓名）
    if user.first_name:
        student = Student.objects.filter(name=user.first_name).first()
        if student:
            return student.id

    # 方法3: 兼容旧账号（student_1）
    if user.username.startswith('student_'):
        try:
            student_id = int(user.username.split('_')[1])
            student = Student.objects.filter(id=student_id).first()
            if student:
                return student.id
        except (ValueError, IndexError):
            pass

    # 方法4: 通过 profile 关联 (如果存在)
    try:
        profile = getattr(user, 'profile', None)
        if profile and hasattr(profile, 'employee_no') and profile.employee_no:
            student = Student.objects.filter(student_no=profile.employee_no).first()
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
        user = self.request.user

        # 筛选参数
        risk_level = self.request.query_params.get('risk_level')
        status = self.request.query_params.get('status')
        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')

        # 根据用户角色过滤数据
        if hasattr(user, 'role'):
            if user.role == 'student':
                # 学生只能看到自己的预警
                student_id = get_student_from_user(user)
                if student_id:
                    queryset = queryset.filter(student_id=student_id)
            elif user.role == 'counselor':
                # 辅导员只能看到自己管理班级的学生预警
                counselor_student_ids = self._get_counselor_student_ids(user)
                if counselor_student_ids:
                    queryset = queryset.filter(student_id__in=counselor_student_ids)
        elif user.is_staff or user.is_superuser:
            # 管理员可以看到所有预警
            pass
        else:
            # 如果没有角色信息，尝试从学生关联
            if not student_id:
                student_id = get_student_from_user(user)
                if student_id:
                    queryset = queryset.filter(student_id=student_id)

        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        if status:
            queryset = queryset.filter(status=status)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.select_related('student', 'course')

    def _get_counselor_student_ids(self, user):
        from users.utils import get_counselor_student_ids
        return get_counselor_student_ids(user)


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
        user = request.user
        queryset = WarningRecord.objects.all()

        # 根据用户角色过滤数据
        is_admin = user.is_staff or user.is_superuser

        if not is_admin and self._is_counselor(user):
            # 辅导员只能看到自己管理班级的学生预警
            counselor_student_ids = self._get_counselor_student_ids(user)
            if counselor_student_ids:
                queryset = queryset.filter(student_id__in=counselor_student_ids)
            else:
                # 如果没有管理班级，返回空统计
                return Response({
                    'code': 200,
                    'message': '获取成功',
                    'data': {
                        'total_warnings': 0,
                        'high_risk_count': 0,
                        'medium_risk_count': 0,
                        'low_risk_count': 0,
                        'normal_count': 0,
                        'active_count': 0,
                        'resolved_count': 0
                    }
                })
        # 管理员可以看到所有预警（不做过滤）

        stats = queryset.aggregate(
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

    def _is_counselor(self, user):
        """检查用户是否是辅导员"""
        # 方法1: 检查是否有counselor_profile属性
        if hasattr(user, 'counselor_profile') and user.counselor_profile:
            return True
        # 方法2: 检查用户组
        if hasattr(user, 'groups'):
            return user.groups.filter(name='counselor').exists()
        return False

    def _get_counselor_student_ids(self, user):
        from users.utils import get_counselor_student_ids
        return get_counselor_student_ids(user)


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


class StudentWarningSummaryView(APIView):
    """
    获取按学生汇总的预警数据
    返回辅导员管理的所有学生及其预警信息，按风险等级排序（高危→中等→低危→正常）
    管理员可以查看所有学生
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 检查是否是辅导员或管理员
        is_counselor = False
        is_admin = user.is_staff or user.is_superuser

        if not is_admin:
            if hasattr(user, 'counselor_profile') and user.counselor_profile:
                is_counselor = True
            elif hasattr(user, 'groups'):
                is_counselor = user.groups.filter(name='counselor').exists()

            if not is_counselor:
                return Response({
                    'code': 403,
                    'message': '只有辅导员或管理员可以访问此接口'
                }, status=status.HTTP_403_FORBIDDEN)

        # 获取学生范围：管理员看所有，辅导员看管理的班级
        if is_admin:
            all_students = Student.objects.all()
        else:
            # 获取辅导员管理的所有学生
            from classes.models import Class

            managed_classes = Class.objects.filter(counselor_id=user.id)
            class_ids = [c.id for c in managed_classes]

            if not class_ids:
                return Response({
                    'code': 200,
                    'message': '获取成功',
                    'data': {
                        'students': [],
                        'total': 0,
                        'risk_summary': {'high': 0, 'medium': 0, 'low': 0, 'normal': 0}
                    }
                })

            all_students = Student.objects.filter(class_id__in=class_ids)

        # 获取这些学生的所有预警记录
        student_ids = [s.id for s in all_students]
        warnings = WarningRecord.objects.filter(
            student_id__in=student_ids
        ).select_related('student', 'course')

        # 按学生分组整理数据
        student_warnings_map = {}
        for warning in warnings:
            sid = warning.student_id
            if sid not in student_warnings_map:
                student_warnings_map[sid] = []
            student_warnings_map[sid].append(warning)

        # 构建学生预警汇总列表
        result = []
        risk_summary = {'high': 0, 'medium': 0, 'low': 0, 'normal': 0}

        for student in all_students:
            student_warnings = student_warnings_map.get(student.id, [])

            if student_warnings:
                # 计算该学生的风险统计
                risk_count = {'high': 0, 'medium': 0, 'low': 0}
                highest_risk = 'low'
                risk_order = {'high': 3, 'medium': 2, 'low': 1}
                total_score = 0

                for w in student_warnings:
                    if w.risk_level in risk_count:
                        risk_count[w.risk_level] += 1
                    # 更新最高风险
                    if risk_order.get(w.risk_level, 0) > risk_order.get(highest_risk, 0):
                        highest_risk = w.risk_level
                    total_score += float(w.composite_score or 0)

                avg_score = total_score / len(student_warnings) if student_warnings else 0

                # 统计风险分布
                risk_summary[highest_risk] += 1

                result.append({
                    'student': {
                        'id': student.id,
                        'name': student.name,
                        'student_no': student.student_no,
                        'class_name': student.class_name if hasattr(student, 'class_name') else str(student.class_field) if hasattr(student, 'class_field') else None
                    },
                    'warnings': [
                        {
                            'id': w.id,
                            'course': {
                                'id': w.course.id if w.course else None,
                                'name': w.course.name if w.course else '未知课程'
                            },
                            'risk_level': w.risk_level,
                            'composite_score': float(w.composite_score) if w.composite_score else None,
                            'attendance_score': float(w.attendance_score) if w.attendance_score else None,
                            'progress_score': float(w.progress_score) if w.progress_score else None,
                            'homework_score': float(w.homework_score) if w.homework_score else None,
                            'exam_score': float(w.exam_score) if w.exam_score else None,
                            'status': w.status,
                            'calculation_time': w.calculation_time.isoformat() if w.calculation_time else None
                        }
                        for w in student_warnings
                    ],
                    'highest_risk': highest_risk,
                    'risk_count': risk_count,
                    'avg_score': round(avg_score, 2),
                    'status': 'at_risk'
                })
            else:
                # 正常学生（无预警）
                risk_summary['normal'] += 1
                result.append({
                    'student': {
                        'id': student.id,
                        'name': student.name,
                        'student_no': student.student_no,
                        'class_name': student.class_name if hasattr(student, 'class_name') else str(student.class_field) if hasattr(student, 'class_field') else None
                    },
                    'warnings': [],
                    'highest_risk': 'normal',
                    'risk_count': {'high': 0, 'medium': 0, 'low': 0},
                    'avg_score': None,
                    'status': 'normal'
                })

        # 按风险等级排序：高危 > 中等 > 低危 > 正常
        # 同风险等级按平均得分升序（分数低的在前）
        risk_order = {'high': 3, 'medium': 2, 'low': 1, 'normal': 0}

        def sort_key(item):
            risk_val = risk_order.get(item['highest_risk'], 0)
            # 平均得分越低越靠前，None放在最后
            score = item['avg_score'] if item['avg_score'] is not None else 999
            return (-risk_val, score)

        result.sort(key=sort_key)

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'students': result,
                'total': len(result),
                'risk_summary': risk_summary
            }
        })
