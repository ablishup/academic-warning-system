"""
特征工程模块

从学习数据中提取特征用于随机森林模型
"""

import pandas as pd
from django.db.models import Avg, Count, Q, F, Sum, FloatField
from django.db.models.functions import Coalesce

from learning.models import (
    LearningActivity, HomeworkSubmission, ExamResult,
    HomeworkAssignment, ExamAssignment
)
from courses.models import CourseEnrollment


class FeatureExtractor:
    """特征提取器"""

    def __init__(self, student_id=None, course_id=None):
        self.student_id = student_id
        self.course_id = course_id

    def extract_features(self):
        """
        提取学生特征

        Returns:
            dict: 特征字典
        """
        features = {}

        # 1. 出勤率特征 (30%)
        features.update(self._extract_attendance_features())

        # 2. 学习进度特征 (20%)
        features.update(self._extract_progress_features())

        # 3. 作业特征 (30%)
        features.update(self._extract_homework_features())

        # 4. 考试特征 (20%)
        features.update(self._extract_exam_features())

        # 5. 综合行为特征
        features.update(self._extract_behavior_features())

        return features

    def _extract_attendance_features(self):
        """提取出勤相关特征"""
        activities = LearningActivity.objects.filter(
            activity_type='sign_in'
        )

        if self.student_id:
            activities = activities.filter(student_id=self.student_id)
        if self.course_id:
            activities = activities.filter(course_id=self.course_id)

        # 计算出勤率
        total_sign_ins = activities.count()
        attended = activities.filter(score__gte=0).count()  # 有分数表示出席

        attendance_rate = (attended / total_sign_ins * 100) if total_sign_ins > 0 else 100

        return {
            'attendance_rate': attendance_rate,
            'total_sign_ins': total_sign_ins,
            'attended_count': attended,
        }

    def _extract_progress_features(self):
        """提取学习进度特征"""
        activities = LearningActivity.objects.filter(
            activity_type='video'
        )

        if self.student_id:
            activities = activities.filter(student_id=self.student_id)
        if self.course_id:
            activities = activities.filter(course_id=self.course_id)

        # 视频学习统计
        stats = activities.aggregate(
            avg_progress=Coalesce(Avg('progress'), 0, output_field=FloatField()),
            total_videos=Count('id'),
            completed_videos=Count('id', filter=Q(progress__gte=90)),
            total_duration=Coalesce(Sum('duration'), 0, output_field=FloatField()),
        )

        return {
            'video_progress': float(stats['avg_progress'] or 0),
            'total_videos': stats['total_videos'],
            'completed_videos': stats['completed_videos'],
            'video_completion_rate': (
                stats['completed_videos'] / stats['total_videos'] * 100
                if stats['total_videos'] > 0 else 0
            ),
            'total_learning_duration': stats['total_duration'] or 0,
        }

    def _extract_homework_features(self):
        """提取作业相关特征"""
        submissions = HomeworkSubmission.objects.all()

        if self.student_id:
            submissions = submissions.filter(student_id=self.student_id)
        if self.course_id:
            submissions = submissions.filter(assignment__course_id=self.course_id)

        # 作业统计
        stats = submissions.aggregate(
            avg_score=Coalesce(Avg('score'), 0, output_field=FloatField()),
            submit_count=Count('id'),
            late_count=Count('id', filter=Q(is_late=1)),
            full_score_count=Count('id', filter=Q(score__gte=90)),
        )

        # 获取应提交作业总数
        assignments = HomeworkAssignment.objects.all()
        if self.course_id:
            assignments = assignments.filter(course_id=self.course_id)

        total_assignments = assignments.count()

        return {
            'homework_avg_score': float(stats['avg_score'] or 0),
            'homework_submit_count': stats['submit_count'],
            'homework_total_count': total_assignments,
            'homework_submit_rate': (
                stats['submit_count'] / total_assignments * 100
                if total_assignments > 0 else 0
            ),
            'homework_late_rate': (
                stats['late_count'] / stats['submit_count'] * 100
                if stats['submit_count'] > 0 else 0
            ),
            'homework_full_score_rate': (
                stats['full_score_count'] / stats['submit_count'] * 100
                if stats['submit_count'] > 0 else 0
            ),
        }

    def _extract_exam_features(self):
        """提取考试相关特征"""
        results = ExamResult.objects.all()

        if self.student_id:
            results = results.filter(student_id=self.student_id)
        if self.course_id:
            results = results.filter(exam__course_id=self.course_id)

        # 考试统计
        stats = results.aggregate(
            avg_score=Coalesce(Avg('score'), 0, output_field=FloatField()),
            exam_count=Count('id'),
            pass_count=Count('id', filter=Q(score__gte=60)),
            high_score_count=Count('id', filter=Q(score__gte=90)),
            max_score=Coalesce(Avg('score'), 0, output_field=FloatField()),
            min_score=Coalesce(Avg('score'), 0, output_field=FloatField()),
        )

        # 获取应参加考试总数
        exams = ExamAssignment.objects.all()
        if self.course_id:
            exams = exams.filter(course_id=self.course_id)

        total_exams = exams.count()

        return {
            'exam_avg_score': float(stats['avg_score'] or 0),
            'exam_count': stats['exam_count'],
            'exam_total_count': total_exams,
            'exam_attendance_rate': (
                stats['exam_count'] / total_exams * 100
                if total_exams > 0 else 0
            ),
            'exam_pass_rate': (
                stats['pass_count'] / stats['exam_count'] * 100
                if stats['exam_count'] > 0 else 0
            ),
            'exam_high_score_rate': (
                stats['high_score_count'] / stats['exam_count'] * 100
                if stats['exam_count'] > 0 else 0
            ),
        }

    def _extract_behavior_features(self):
        """提取学习行为特征"""
        activities = LearningActivity.objects.all()

        if self.student_id:
            activities = activities.filter(student_id=self.student_id)
        if self.course_id:
            activities = activities.filter(course_id=self.course_id)

        # 学习活跃度
        total_activities = activities.count()

        # 计算每日平均学习时长（分钟）
        from django.db.models.functions import TruncDate

        daily_stats = activities.annotate(
            date=TruncDate('start_time')
        ).values('date').annotate(
            daily_duration=Sum('duration')
        ).aggregate(
            avg_daily_duration=Coalesce(Avg('daily_duration'), 0, output_field=FloatField())
        )

        return {
            'total_activities': total_activities,
            'avg_daily_learning_minutes': float(daily_stats['avg_daily_duration'] or 0) / 60,
        }


class FeatureEngineering:
    """特征工程"""

    # 特征权重配置（与业务权重一致）
    FEATURE_WEIGHTS = {
        'attendance': 0.30,
        'progress': 0.20,
        'homework': 0.30,
        'exam': 0.20,
    }

    @classmethod
    def get_feature_names(cls):
        """获取所有特征名称"""
        return [
            # 出勤特征
            'attendance_rate',
            # 进度特征
            'video_progress',
            'video_completion_rate',
            # 作业特征
            'homework_avg_score',
            'homework_submit_rate',
            'homework_late_rate',
            # 考试特征
            'exam_avg_score',
            'exam_pass_rate',
            'exam_attendance_rate',
            # 行为特征
            'avg_daily_learning_minutes',
        ]

    @classmethod
    def calculate_composite_score(cls, features):
        """
        计算综合得分（加权平均）

        Args:
            features: 特征字典

        Returns:
            float: 综合得分 (0-100)
        """
        # 出勤得分
        attendance_score = features.get('attendance_rate', 0)

        # 进度得分
        progress_score = features.get('video_progress', 0)

        # 作业得分
        homework_score = features.get('homework_avg_score', 0)

        # 考试得分
        exam_score = features.get('exam_avg_score', 0)

        # 加权计算
        composite = (
            attendance_score * cls.FEATURE_WEIGHTS['attendance'] +
            progress_score * cls.FEATURE_WEIGHTS['progress'] +
            homework_score * cls.FEATURE_WEIGHTS['homework'] +
            exam_score * cls.FEATURE_WEIGHTS['exam']
        )

        return round(composite, 2)

    @classmethod
    def determine_risk_level(cls, score):
        """
        根据综合得分确定风险等级

        Args:
            score: 综合得分

        Returns:
            str: 风险等级 (high, medium, low, normal)
        """
        # 阈值基于2026-04-27导入的真实数据分布 (mean=74, max=85)
        # score < 65: ~5%高危, score 65-75: ~35%中危, score 75-80: ~45%低危, score >= 80: ~15%正常
        if score < 65:
            return 'high'  # 红色预警
        elif score < 75:
            return 'medium'  # 橙色预警
        elif score < 80:
            return 'low'  # 黄色预警
        else:
            return 'normal'  # 正常
