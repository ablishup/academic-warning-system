"""
数据同步模块

将原始学习数据同步到 StudentCourseScore 表
"""

from django.db.models import Avg, Count, Q, Sum, FloatField
from django.db.models.functions import Coalesce

from classes.models import Student
from courses.models import Course, CourseEnrollment
from learning.models import LearningActivity, HomeworkSubmission, ExamResult
from .models import StudentCourseScore


class DataSynchronizer:
    """数据同步器"""

    @classmethod
    def sync_all_students_scores(cls):
        """
        同步所有学生的课程得分
        遍历所有学生-课程组合，计算综合得分
        """
        results = []

        # 获取所有选课关系
        enrollments = CourseEnrollment.objects.all()

        for enrollment in enrollments:
            try:
                score = cls.calculate_student_course_score(
                    enrollment.student_id,
                    enrollment.course_id
                )
                results.append({
                    'student_id': enrollment.student_id,
                    'course_id': enrollment.course_id,
                    'status': 'success',
                    'score': score
                })
            except Exception as e:
                results.append({
                    'student_id': enrollment.student_id,
                    'course_id': enrollment.course_id,
                    'status': 'error',
                    'error': str(e)
                })

        return results

    @classmethod
    def calculate_student_course_score(cls, student_id, course_id):
        """
        计算单个学生的单门课程综合得分

        Returns:
            StudentCourseScore: 得分记录
        """
        # 1. 计算出勤率
        attendance_activities = LearningActivity.objects.filter(
            student_id=student_id,
            course_id=course_id,
            activity_type='sign_in'
        )
        total_attendance = attendance_activities.count()
        attended = attendance_activities.filter(score__gte=0).count()
        attendance_rate = (attended / total_attendance * 100) if total_attendance > 0 else 100

        # 2. 计算视频进度
        video_activities = LearningActivity.objects.filter(
            student_id=student_id,
            course_id=course_id,
            activity_type='video'
        )
        video_stats = video_activities.aggregate(
            avg_progress=Coalesce(Avg('progress'), 0, output_field=FloatField()),
            total_videos=Count('id')
        )
        video_progress = float(video_stats['avg_progress'] or 0)

        # 3. 计算作业平均分
        homework_submissions = HomeworkSubmission.objects.filter(
            student_id=student_id,
            assignment__course_id=course_id
        )
        homework_stats = homework_submissions.aggregate(
            avg_score=Coalesce(Avg('score'), 0, output_field=FloatField()),
            submit_count=Count('id')
        )
        homework_avg = float(homework_stats['avg_score'] or 0)

        # 计算作业提交率
        from learning.models import HomeworkAssignment
        total_assignments = HomeworkAssignment.objects.filter(course_id=course_id).count()
        homework_submit_rate = (
            homework_stats['submit_count'] / total_assignments * 100
            if total_assignments > 0 else 0
        )

        # 4. 计算考试平均分
        exam_results = ExamResult.objects.filter(
            student_id=student_id,
            exam__course_id=course_id
        )
        exam_stats = exam_results.aggregate(
            avg_score=Coalesce(Avg('score'), 0, output_field=FloatField())
        )
        exam_avg = float(exam_stats['avg_score'] or 0)

        # 5. 保存或更新得分记录
        score_record, created = StudentCourseScore.objects.update_or_create(
            student_id=student_id,
            course_id=course_id,
            defaults={
                'attendance_rate': attendance_rate,
                'video_progress': video_progress,
                'homework_avg': homework_avg,
                'homework_submit_rate': homework_submit_rate,
                'exam_avg': exam_avg,
            }
        )

        return score_record

    @classmethod
    def get_sync_statistics(cls):
        """获取同步统计信息"""
        total_students = Student.objects.count()
        total_courses = Course.objects.count()
        total_scores = StudentCourseScore.objects.count()

        # 计算覆盖率
        total_enrollments = CourseEnrollment.objects.count()
        coverage = (total_scores / total_enrollments * 100) if total_enrollments > 0 else 0

        return {
            'total_students': total_students,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'synced_scores': total_scores,
            'coverage_percent': round(coverage, 2)
        }
