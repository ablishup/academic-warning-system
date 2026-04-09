# import_app/views.py
import os
import io
import pandas as pd
from django.db import transaction
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import Student
from courses.models import Course
from learning.models import (
    LearningActivity, HomeworkAssignment, HomeworkSubmission,
    ExamAssignment, ExamResult
)
from .models import ImportLog


class ImportTemplateDownloadView(APIView):
    """下载导入模板视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        import_type = request.query_params.get('type')
        if not import_type:
            return Response({
                'code': 400,
                'message': '需要指定type参数'
            }, status=status.HTTP_400_BAD_REQUEST)

        templates = {
            'activities': {
                'filename': '学习活动导入模板.xlsx',
                'columns': ['学号', '姓名', '活动类型', '活动名称', '时长(秒)', '进度(%)', '得分', '日期']
            },
            'homework': {
                'filename': '作业成绩导入模板.xlsx',
                'columns': ['学号', '姓名', '作业标题', '得分', '提交时间', '是否迟交']
            },
            'exams': {
                'filename': '考试成绩导入模板.xlsx',
                'columns': ['学号', '姓名', '考试标题', '得分', '提交时间']
            },
            'enrollments': {
                'filename': '选课关系导入模板.xlsx',
                'columns': ['学号', '姓名', '课程编号', '课程名称']
            }
        }

        if import_type not in templates:
            return Response({
                'code': 400,
                'message': '不支持的模板类型'
            }, status=status.HTTP_400_BAD_REQUEST)

        template = templates[import_type]

        # 创建示例数据
        sample_data = {
            'activities': [
                ['2021001', '张三', 'video', '第一章视频', '1800', '85.5', '', '2024-03-15'],
                ['2021002', '李四', 'sign_in', '第3周签到', '300', '100', '', '2024-03-15'],
            ],
            'homework': [
                ['2021001', '张三', '第一次作业', '85', '2024-03-10 10:30:00', '否'],
                ['2021002', '李四', '第一次作业', '92', '2024-03-10 09:15:00', '否'],
            ],
            'exams': [
                ['2021001', '张三', '期中考试', '78', '2024-04-01 14:00:00'],
                ['2021002', '李四', '期中考试', '88', '2024-04-01 14:00:00'],
            ],
            'enrollments': [
                ['2021001', '张三', 'CS101', '数据结构'],
                ['2021002', '李四', 'CS101', '数据结构'],
            ]
        }

        # 创建Excel文件
        output = io.BytesIO()
        df = pd.DataFrame(sample_data.get(import_type, []), columns=template['columns'])

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='数据', index=False)

        output.seek(0)

        response = Response(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{template["filename"]}"'
        return response


class BaseImportView(APIView):
    """基础导入视图"""
    permission_classes = [IsAuthenticated]
    import_type = None

    def post(self, request):
        # 检查文件
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({
                'code': 400,
                'message': '请上传文件'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 检查文件类型
        if not file_obj.name.endswith(('.xlsx', '.xls')):
            return Response({
                'code': 400,
                'message': '只支持Excel文件(.xlsx, .xls)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取课程ID
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({
                'code': 400,
                'message': '需要指定course_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证课程存在
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'code': 404,
                'message': '课程不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 创建导入记录
        import_log = ImportLog.objects.create(
            import_type=self.import_type,
            file_name=file_obj.name,
            file_size=file_obj.size,
            uploaded_by=request.user,
            course_id=course_id,
            status='pending'
        )

        try:
            # 读取Excel文件
            df = pd.read_excel(file_obj)
            import_log.total_rows = len(df)

            # 根据类型执行导入
            if self.import_type == 'activities':
                result = self.import_activities(df, course_id, import_log)
            elif self.import_type == 'homework':
                result = self.import_homework(df, course_id, import_log)
            elif self.import_type == 'exams':
                result = self.import_exams(df, course_id, import_log)
            elif self.import_type == 'enrollments':
                result = self.import_enrollments(df, import_log)
            else:
                raise ValueError(f'不支持的导入类型: {self.import_type}')

            return Response({
                'code': 200,
                'message': '导入完成',
                'data': {
                    'import_id': import_log.id,
                    'total_rows': import_log.total_rows,
                    'success_rows': import_log.success_rows,
                    'failed_rows': import_log.failed_rows,
                    'status': import_log.status,
                    'details': result
                }
            })

        except Exception as e:
            import_log.status = 'failed'
            import_log.error_message = str(e)
            import_log.save()

            return Response({
                'code': 500,
                'message': f'导入失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def import_activities(self, df, course_id, import_log):
        """导入学习活动数据"""
        success_count = 0
        failed_records = []

        # 必需的列
        required_columns = ['学号', '活动类型', '活动名称']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f'缺少必需列: {col}')

        activity_type_mapping = {
            '视频': 'video',
            'video': 'video',
            '签到': 'sign_in',
            'sign_in': 'sign_in',
            '讨论': 'discuss',
            'discuss': 'discuss',
            '测验': 'quiz',
            'quiz': 'quiz',
        }

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    student_no = str(row.get('学号', '')).strip()
                    activity_type_raw = str(row.get('活动类型', '')).strip()
                    activity_name = str(row.get('活动名称', '')).strip()

                    # 查找学生
                    try:
                        student = Student.objects.get(student_no=student_no)
                    except Student.DoesNotExist:
                        failed_records.append({
                            'row': index + 2,
                            'error': f'学生不存在: {student_no}'
                        })
                        continue

                    # 转换活动类型
                    activity_type = activity_type_mapping.get(activity_type_raw, 'other')

                    # 解析其他字段
                    duration = self._parse_int(row.get('时长(秒)', 0))
                    progress = self._parse_float(row.get('进度(%)', 100))
                    score = self._parse_float(row.get('得分')) if pd.notna(row.get('得分')) else None

                    # 创建学习活动记录
                    LearningActivity.objects.create(
                        student=student,
                        course_id=course_id,
                        activity_type=activity_type,
                        activity_name=activity_name,
                        duration=duration,
                        progress=progress,
                        score=score,
                        start_time=timezone.now(),
                        end_time=timezone.now(),
                        raw_data={'imported': True, 'row_num': index + 2}
                    )

                    success_count += 1

                except Exception as e:
                    failed_records.append({
                        'row': index + 2,
                        'error': str(e)
                    })

        import_log.success_rows = success_count
        import_log.failed_rows = len(failed_records)
        import_log.status = 'success' if not failed_records else 'partial'
        import_log.details = {'failed_records': failed_records}
        import_log.save()

        return {'failed_records': failed_records}

    def import_homework(self, df, course_id, import_log):
        """导入作业数据"""
        success_count = 0
        failed_records = []

        required_columns = ['学号', '作业标题', '得分']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f'缺少必需列: {col}')

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    student_no = str(row.get('学号', '')).strip()
                    homework_title = str(row.get('作业标题', '')).strip()
                    score = self._parse_float(row.get('得分', 0))

                    # 查找学生
                    try:
                        student = Student.objects.get(student_no=student_no)
                    except Student.DoesNotExist:
                        failed_records.append({
                            'row': index + 2,
                            'error': f'学生不存在: {student_no}'
                        })
                        continue

                    # 查找或创建作业任务
                    assignment, _ = HomeworkAssignment.objects.get_or_create(
                        course_id=course_id,
                        title=homework_title,
                        defaults={
                            'full_score': 100,
                            'start_time': timezone.now(),
                            'deadline': timezone.now(),
                            'status': 1
                        }
                    )

                    # 创建或更新作业提交记录
                    HomeworkSubmission.objects.update_or_create(
                        student=student,
                        assignment=assignment,
                        defaults={
                            'score': score,
                            'submit_time': timezone.now(),
                            'is_late': False
                        }
                    )

                    success_count += 1

                except Exception as e:
                    failed_records.append({
                        'row': index + 2,
                        'error': str(e)
                    })

        import_log.success_rows = success_count
        import_log.failed_rows = len(failed_records)
        import_log.status = 'success' if not failed_records else 'partial'
        import_log.details = {'failed_records': failed_records}
        import_log.save()

        return {'failed_records': failed_records}

    def import_exams(self, df, course_id, import_log):
        """导入考试数据"""
        success_count = 0
        failed_records = []

        required_columns = ['学号', '考试标题', '得分']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f'缺少必需列: {col}')

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    student_no = str(row.get('学号', '')).strip()
                    exam_title = str(row.get('考试标题', '')).strip()
                    score = self._parse_float(row.get('得分', 0))

                    # 查找学生
                    try:
                        student = Student.objects.get(student_no=student_no)
                    except Student.DoesNotExist:
                        failed_records.append({
                            'row': index + 2,
                            'error': f'学生不存在: {student_no}'
                        })
                        continue

                    # 查找或创建考试任务
                    exam, _ = ExamAssignment.objects.get_or_create(
                        course_id=course_id,
                        title=exam_title,
                        defaults={
                            'full_score': 100,
                            'exam_type': 'quiz',
                            'start_time': timezone.now(),
                            'end_time': timezone.now(),
                            'status': 1
                        }
                    )

                    # 创建或更新考试结果
                    ExamResult.objects.update_or_create(
                        student=student,
                        exam=exam,
                        defaults={
                            'score': score,
                            'submit_time': timezone.now(),
                            'is_submitted': True
                        }
                    )

                    success_count += 1

                except Exception as e:
                    failed_records.append({
                        'row': index + 2,
                        'error': str(e)
                    })

        import_log.success_rows = success_count
        import_log.failed_rows = len(failed_records)
        import_log.status = 'success' if not failed_records else 'partial'
        import_log.details = {'failed_records': failed_records}
        import_log.save()

        return {'failed_records': failed_records}

    def import_enrollments(self, df, import_log):
        """导入选课关系"""
        from courses.models import CourseEnrollment

        success_count = 0
        failed_records = []

        required_columns = ['学号', '课程编号']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f'缺少必需列: {col}')

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    student_no = str(row.get('学号', '')).strip()
                    course_no = str(row.get('课程编号', '')).strip()

                    # 查找学生
                    try:
                        student = Student.objects.get(student_no=student_no)
                    except Student.DoesNotExist:
                        failed_records.append({
                            'row': index + 2,
                            'error': f'学生不存在: {student_no}'
                        })
                        continue

                    # 查找课程
                    try:
                        course = Course.objects.get(course_no=course_no)
                    except Course.DoesNotExist:
                        failed_records.append({
                            'row': index + 2,
                            'error': f'课程不存在: {course_no}'
                        })
                        continue

                    # 创建选课关系
                    CourseEnrollment.objects.get_or_create(
                        student_id=student.id,
                        course_id=course.id,
                        defaults={
                            'enroll_time': timezone.now(),
                            'status': 1
                        }
                    )

                    success_count += 1

                except Exception as e:
                    failed_records.append({
                        'row': index + 2,
                        'error': str(e)
                    })

        import_log.success_rows = success_count
        import_log.failed_rows = len(failed_records)
        import_log.status = 'success' if not failed_records else 'partial'
        import_log.details = {'failed_records': failed_records}
        import_log.save()

        return {'failed_records': failed_records}

    def _parse_int(self, value, default=0):
        """解析整数"""
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def _parse_float(self, value, default=0.0):
        """解析浮点数"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default


class ActivityImportView(BaseImportView):
    """学习活动导入视图"""
    import_type = 'activities'


class HomeworkImportView(BaseImportView):
    """作业数据导入视图"""
    import_type = 'homework'


class ExamImportView(BaseImportView):
    """考试数据导入视图"""
    import_type = 'exams'


class EnrollmentImportView(BaseImportView):
    """选课关系导入视图"""
    import_type = 'enrollments'


class ImportLogListView(generics.ListAPIView):
    """导入记录列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = None  # 稍后定义

    def get_queryset(self):
        queryset = ImportLog.objects.all()

        import_type = self.request.query_params.get('type')
        if import_type:
            queryset = queryset.filter(import_type=import_type)

        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.select_related('uploaded_by')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for log in queryset:
            data.append({
                'id': log.id,
                'import_type': log.import_type,
                'import_type_display': log.get_import_type_display(),
                'file_name': log.file_name,
                'file_size': log.file_size,
                'total_rows': log.total_rows,
                'success_rows': log.success_rows,
                'failed_rows': log.failed_rows,
                'status': log.status,
                'status_display': log.get_status_display(),
                'uploaded_by': log.uploaded_by.username if log.uploaded_by else None,
                'created_at': log.created_at,
            })

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': data
        })
