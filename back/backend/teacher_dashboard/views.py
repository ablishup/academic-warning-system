# teacher_dashboard/views.py
from django.db.models import Avg, Count, Q, Max, Min
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import Student
from courses.models import Course, CourseEnrollment
from learning.models import (
    LearningActivity, HomeworkAssignment, HomeworkSubmission,
    ExamAssignment, ExamResult
)
from warning_system.models import WarningRecord


class TeacherCourseListView(APIView):
    """教师课程列表视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取当前教师教授的课程列表"""
        # 从用户信息获取教师ID
        # 假设request.user.id对应teacher_id
        teacher_id = request.user.id

        courses = Course.objects.filter(teacher_id=teacher_id)

        data = []
        for course in courses:
            # 获取学生人数
            student_count = CourseEnrollment.objects.filter(
                course_id=course.id
            ).count()

            # 获取预警学生数
            warning_count = WarningRecord.objects.filter(
                course_id=course.id,
                status='active'
            ).count()

            data.append({
                'id': course.id,
                'name': course.name,
                'course_no': course.course_no,
                'credit': str(course.credit),
                'semester': course.semester,
                'student_count': student_count,
                'warning_count': warning_count,
            })

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': data
        })


class TeacherCourseStudentsView(APIView):
    """教师课程学生列表视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        """获取指定课程的学生列表（含学情概要）"""
        # 验证课程存在
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'code': 404,
                'message': '课程不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 获取课程的所有学生
        enrollments = CourseEnrollment.objects.filter(
            course_id=course_id
        )

        data = []
        for enrollment in enrollments:
            # 查询学生信息
            try:
                student = Student.objects.get(id=enrollment.student_id)
            except Student.DoesNotExist:
                continue

            # 计算学习活动统计
            activity_stats = LearningActivity.objects.filter(
                student_id=student.id,
                course_id=course_id
            ).aggregate(
                total_duration=Avg('duration'),
                avg_progress=Avg('progress'),
                activity_count=Count('id')
            )

            # 计算作业统计
            homework_stats = HomeworkSubmission.objects.filter(
                student_id=student.id,
                assignment__course_id=course_id
            ).aggregate(
                avg_score=Avg('score'),
                submit_count=Count('id')
            )

            # 计算考试统计
            exam_stats = ExamResult.objects.filter(
                student_id=student.id,
                exam__course_id=course_id
            ).aggregate(
                avg_score=Avg('score'),
                exam_count=Count('id')
            )

            # 获取当前预警等级
            warning = WarningRecord.objects.filter(
                student_id=student.id,
                course_id=course_id,
                status='active'
            ).first()

            # 计算综合得分（用于排序）
            composite_score = self._calculate_composite_score(
                activity_stats['avg_progress'] or 0,
                homework_stats['avg_score'] or 0,
                exam_stats['avg_score'] or 0
            )

            data.append({
                'id': student.id,
                'student_no': student.student_no,
                'name': student.name,
                'gender': student.gender,
                'enroll_time': enrollment.enroll_time,
                'learning_stats': {
                    'activity_count': activity_stats['activity_count'],
                    'avg_progress': round(activity_stats['avg_progress'] or 0, 2),
                    'total_duration': int(activity_stats['total_duration'] or 0),
                },
                'homework_stats': {
                    'submit_count': homework_stats['submit_count'],
                    'avg_score': round(homework_stats['avg_score'] or 0, 2),
                },
                'exam_stats': {
                    'exam_count': exam_stats['exam_count'],
                    'avg_score': round(exam_stats['avg_score'] or 0, 2),
                },
                'composite_score': round(composite_score, 2),
                'warning_level': warning.risk_level if warning else None,
                'warning_status': warning.status if warning else None,
            })

        # 按综合得分排序（低分在前，预警优先）
        data.sort(key=lambda x: (x['composite_score'], x['warning_level'] or ''))

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'course': {
                    'id': course.id,
                    'name': course.name,
                    'course_no': course.course_no,
                    'student_count': len(data),
                },
                'students': data
            }
        })

    def _calculate_composite_score(self, progress, homework_score, exam_score):
        """计算综合得分"""
        # 权重：视频进度20%，作业30%，考试50%
        progress_weight = 0.2
        homework_weight = 0.3
        exam_weight = 0.5

        return (
            float(progress) * progress_weight +
            float(homework_score) * homework_weight +
            float(exam_score) * exam_weight
        )


class TeacherStudentSummaryView(APIView):
    """教师查看学生学情详情视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        """获取指定学生的详细学情"""
        course_id = request.GET.get('course_id') or request.query_params.get('course_id')

        # 验证学生存在
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({
                'code': 404,
                'message': '学生不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 基本信息
        data = {
            'id': student.id,
            'student_no': student.student_no,
            'name': student.name,
            'gender': student.gender,
            'class_id': student.class_id,
            'major_id': student.major_id,
        }

        # 如果指定了课程，返回课程详情
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '课程不存在'
                }, status=status.HTTP_404_NOT_FOUND)

            data['course'] = {
                'id': course.id,
                'name': course.name,
                'course_no': course.course_no,
            }

            # 学习活动详情
            activities = LearningActivity.objects.filter(
                student_id=student_id,
                course_id=course_id
            ).order_by('-start_time')[:10]

            data['recent_activities'] = [{
                'id': act.id,
                'type': act.get_activity_type_display(),
                'name': act.activity_name,
                'duration': act.duration,
                'progress': str(act.progress),
                'score': str(act.score) if act.score else None,
                'start_time': act.start_time,
            } for act in activities]

            # 学习活动统计
            activity_stats = LearningActivity.objects.filter(
                student_id=student_id,
                course_id=course_id
            ).aggregate(
                total_duration=Avg('duration'),
                avg_progress=Avg('progress'),
                video_count=Count('id', filter=Q(activity_type='video')),
                sign_in_count=Count('id', filter=Q(activity_type='sign_in')),
            )

            data['activity_summary'] = {
                'video_count': activity_stats['video_count'],
                'sign_in_count': activity_stats['sign_in_count'],
                'avg_progress': round(activity_stats['avg_progress'] or 0, 2),
                'total_duration': int(activity_stats['total_duration'] or 0),
            }

            # 作业详情
            homework_submissions = HomeworkSubmission.objects.filter(
                student_id=student_id,
                assignment__course_id=course_id
            ).select_related('assignment').order_by('-submit_time')[:5]

            data['homework_records'] = [{
                'id': sub.id,
                'title': sub.assignment.title,
                'score': str(sub.score),
                'full_score': str(sub.assignment.full_score),
                'submit_time': sub.submit_time,
                'is_late': sub.is_late,
            } for sub in homework_submissions]

            # 作业统计
            homework_stats = HomeworkSubmission.objects.filter(
                student_id=student_id,
                assignment__course_id=course_id
            ).aggregate(
                avg_score=Avg('score'),
                submit_count=Count('id'),
                late_count=Count('id', filter=Q(is_late=True)),
            )

            total_homework = HomeworkAssignment.objects.filter(
                course_id=course_id
            ).count()

            data['homework_summary'] = {
                'total': total_homework,
                'submitted': homework_stats['submit_count'],
                'avg_score': round(homework_stats['avg_score'] or 0, 2),
                'late_count': homework_stats['late_count'],
                'completion_rate': round(
                    (homework_stats['submit_count'] / total_homework * 100), 2
                ) if total_homework > 0 else 0,
            }

            # 考试详情
            exam_results = ExamResult.objects.filter(
                student_id=student_id,
                exam__course_id=course_id
            ).select_related('exam').order_by('-submit_time')

            data['exam_records'] = [{
                'id': res.id,
                'title': res.exam.title,
                'type': res.exam.get_exam_type_display(),
                'score': str(res.score),
                'full_score': str(res.exam.full_score),
                'submit_time': res.submit_time,
            } for res in exam_results]

            # 考试统计
            exam_stats = ExamResult.objects.filter(
                student_id=student_id,
                exam__course_id=course_id
            ).aggregate(
                avg_score=Avg('score'),
                max_score=Max('score'),
                min_score=Min('score'),
                exam_count=Count('id'),
            )

            data['exam_summary'] = {
                'exam_count': exam_stats['exam_count'],
                'avg_score': round(exam_stats['avg_score'] or 0, 2),
                'highest_score': round(exam_stats['max_score'] or 0, 2),
                'lowest_score': round(exam_stats['min_score'] or 0, 2),
            }

            # 预警信息
            warning = WarningRecord.objects.filter(
                student_id=student_id,
                course_id=course_id,
                status='active'
            ).first()

            if warning:
                data['warning'] = {
                    'id': warning.id,
                    'level': warning.risk_level,
                    'level_display': warning.get_risk_level_display(),
                    'composite_score': str(warning.composite_score),
                    'predicted_score': str(warning.predicted_score) if warning.predicted_score else None,
                    'suggestion': warning.suggestion,
                    'created_at': warning.created_at,
                }
            else:
                data['warning'] = None

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': data
        })


class TeacherCourseStatsView(APIView):
    """教师课程统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        """获取课程的整体学情统计"""
        # 验证课程存在
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'code': 404,
                'message': '课程不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 学生总数
        total_students = CourseEnrollment.objects.filter(
            course_id=course_id
        ).count()

        if total_students == 0:
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'course': {
                        'id': course.id,
                        'name': course.name,
                    },
                    'total_students': 0,
                    'note': '该课程暂无学生'
                }
            })

        # 学习活动统计
        activity_stats = LearningActivity.objects.filter(
            course_id=course_id
        ).aggregate(
            avg_progress=Avg('progress'),
            total_activities=Count('id'),
            video_progress=Avg('progress', filter=Q(activity_type='video')),
        )

        # 作业统计
        homework_stats = HomeworkSubmission.objects.filter(
            assignment__course_id=course_id
        ).aggregate(
            avg_score=Avg('score'),
            total_submissions=Count('id'),
        )

        # 考试统计
        exam_stats = ExamResult.objects.filter(
            exam__course_id=course_id
        ).aggregate(
            avg_score=Avg('score'),
            total_results=Count('id'),
        )

        # 预警统计
        warning_stats = WarningRecord.objects.filter(
            course_id=course_id,
            status='active'
        ).values('risk_level').annotate(
            count=Count('id')
        )

        warning_distribution = {
            'high': 0,
            'medium': 0,
            'low': 0,
            'normal': 0,
        }
        for stat in warning_stats:
            level = stat['risk_level']
            if level in warning_distribution:
                warning_distribution[level] = stat['count']

        # 成绩分布
        score_ranges = {
            'excellent': 0,  # 90-100
            'good': 0,       # 80-89
            'average': 0,    # 70-79
            'pass': 0,       # 60-69
            'fail': 0,       # <60
        }

        # 基于作业和考试的综合成绩分布
        student_scores = []
        # 获取选了这门课的所有学生ID
        enrollment_student_ids = CourseEnrollment.objects.filter(
            course_id=course_id
        ).values_list('student_id', flat=True)
        students = Student.objects.filter(id__in=enrollment_student_ids)

        for student in students:
            hw_avg = HomeworkSubmission.objects.filter(
                student=student,
                assignment__course_id=course_id
            ).aggregate(Avg('score'))['score__avg'] or 0

            exam_avg = ExamResult.objects.filter(
                student=student,
                exam__course_id=course_id
            ).aggregate(Avg('score'))['score__avg'] or 0

            # 简单加权：作业30%，考试70%
            final_score = float(hw_avg) * 0.3 + float(exam_avg) * 0.7
            student_scores.append(final_score)

        for score in student_scores:
            if score >= 90:
                score_ranges['excellent'] += 1
            elif score >= 80:
                score_ranges['good'] += 1
            elif score >= 70:
                score_ranges['average'] += 1
            elif score >= 60:
                score_ranges['pass'] += 1
            else:
                score_ranges['fail'] += 1

        # 最近预警学生
        recent_warnings = WarningRecord.objects.filter(
            course_id=course_id,
            status='active'
        ).select_related('student').order_by('-created_at')[:5]

        warning_students = [{
            'student_id': w.student.id,
            'student_name': w.student.name,
            'student_no': w.student.student_no,
            'risk_level': w.risk_level,
            'composite_score': str(w.composite_score),
            'created_at': w.created_at,
        } for w in recent_warnings]

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'course': {
                    'id': course.id,
                    'name': course.name,
                    'course_no': course.course_no,
                },
                'overview': {
                    'total_students': total_students,
                    'avg_video_progress': round(activity_stats['video_progress'] or 0, 2),
                    'avg_homework_score': round(homework_stats['avg_score'] or 0, 2),
                    'avg_exam_score': round(exam_stats['avg_score'] or 0, 2),
                },
                'warning_distribution': warning_distribution,
                'score_distribution': score_ranges,
                'warning_students': warning_students,
            }
        })
