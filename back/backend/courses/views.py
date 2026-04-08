# courses/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from .models import Course, CourseEnrollment, KnowledgePoint
from .serializers import CourseSerializer, KnowledgePointSerializer, CourseListSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_list_view(request):
    """获取课程列表"""
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_detail_view(request, pk):
    """获取课程详情"""
    try:
        course = Course.objects.get(pk=pk)
        serializer = CourseSerializer(course)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })
    except Course.DoesNotExist:
        return Response({
            'code': 404,
            'message': '课程不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_knowledge_points_view(request, course_id):
    """获取课程的知识点列表"""
    points = KnowledgePoint.objects.filter(course_id=course_id)
    serializer = KnowledgePointSerializer(points, many=True)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_courses_view(request):
    """获取教师教授的课程列表"""
    # 假设request.user.id就是teacher_id
    courses = Course.objects.filter(teacher_id=request.user.id)
    serializer = CourseSerializer(courses, many=True)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_courses_view(request):
    """获取学生选修的课程列表"""
    # 获取学生ID（从用户信息或其他方式获取）
    student_id = request.query_params.get('student_id')
    if not student_id:
        return Response({
            'code': 400,
            'message': '缺少student_id参数'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 获取学生选课的课程ID列表
    enrollments = CourseEnrollment.objects.filter(student_id=student_id)
    course_ids = [e.course_id for e in enrollments]
    courses = Course.objects.filter(id__in=course_ids)
    serializer = CourseListSerializer(courses, many=True)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })
