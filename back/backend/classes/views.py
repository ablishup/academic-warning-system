# classes/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Student, Class
from .serializers import StudentSerializer, ClassSerializer, StudentListSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_list_view(request):
    """获取学生列表"""
    # 获取查询参数
    class_id = request.query_params.get('class_id')
    keyword = request.query_params.get('keyword')

    students = Student.objects.all()

    if class_id:
        students = students.filter(class_id=class_id)

    if keyword:
        students = students.filter(
            Q(name__icontains=keyword) |
            Q(student_no__icontains=keyword)
        )

    serializer = StudentSerializer(students, many=True)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_detail_view(request, pk):
    """获取学生详情"""
    try:
        student = Student.objects.get(pk=pk)
        serializer = StudentSerializer(student)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })
    except Student.DoesNotExist:
        return Response({
            'code': 404,
            'message': '学生不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def class_list_view(request):
    """获取班级列表"""
    classes = Class.objects.all()
    serializer = ClassSerializer(classes, many=True)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def class_students_view(request, class_id):
    """获取班级学生列表"""
    students = Student.objects.filter(class_id=class_id)
    serializer = StudentListSerializer(students, many=True)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_search_view(request):
    """搜索学生"""
    keyword = request.query_params.get('q', '')
    if not keyword:
        return Response({
            'code': 400,
            'message': '请输入搜索关键词'
        }, status=status.HTTP_400_BAD_REQUEST)

    students = Student.objects.filter(
        Q(name__icontains=keyword) |
        Q(student_no__icontains=keyword)
    )[:20]  # 限制返回数量

    serializer = StudentListSerializer(students, many=True)
    return Response({
        'code': 200,
        'message': '搜索成功',
        'data': serializer.data
    })
