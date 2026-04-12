import os
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from .models import Course, CourseEnrollment, KnowledgePoint, CourseResource
from .serializers import (
    CourseSerializer, KnowledgePointSerializer, CourseListSerializer,
    CourseResourceSerializer, CourseResourceCreateSerializer
)


class CourseResourceListCreateView(generics.ListCreateAPIView):
    """课程资源列表和创建视图"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CourseResource.objects.all()

        # 筛选参数
        course_id = self.request.query_params.get('course_id')
        resource_type = self.request.query_params.get('resource_type')
        knowledge_point_id = self.request.query_params.get('knowledge_point_id')

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        if knowledge_point_id:
            queryset = queryset.filter(knowledge_point_id=knowledge_point_id)

        return queryset.select_related('course', 'knowledge_point', 'created_by')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseResourceCreateSerializer
        return CourseResourceSerializer

    def perform_create(self, serializer):
        """创建时设置上传者"""
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        """列表响应包装"""
        response = super().list(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': response.data
        })

    def create(self, request, *args, **kwargs):
        """创建响应包装"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # 使用详细序列化器返回完整数据
        detail_serializer = CourseResourceSerializer(
            serializer.instance, context={'request': request}
        )

        return Response({
            'code': 200,
            'message': '上传成功',
            'data': detail_serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class CourseResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """课程资源详情、更新、删除视图"""
    permission_classes = [IsAuthenticated]
    queryset = CourseResource.objects.all()
    serializer_class = CourseResourceSerializer
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        """详情响应包装"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        """更新响应包装"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = CourseResourceCreateSerializer(
            instance, data=request.data, partial=partial
        )
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        # 使用详细序列化器返回完整数据
        detail_serializer = CourseResourceSerializer(
            serializer.instance, context={'request': request}
        )

        return Response({
            'code': 200,
            'message': '更新成功',
            'data': detail_serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """删除响应包装"""
        instance = self.get_object()
        # 删除关联的文件
        if instance.file:
            file_path = instance.file.path
            if os.path.exists(file_path):
                os.remove(file_path)

        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除成功'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_resource_download_view(request, pk):
    """下载课程资源"""
    resource = get_object_or_404(CourseResource, pk=pk)

    if not resource.file:
        return Response({
            'code': 404,
            'message': '文件不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    # 增加下载计数
    resource.download_count += 1
    resource.save(update_fields=['download_count'])

    file_path = resource.file.path
    file_name = os.path.basename(file_path)

    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


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


def get_student_from_user(user):
    """从当前登录用户获取学生ID"""
    if not user or not user.is_authenticated:
        return None

    from classes.models import Student

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_courses_view(request):
    """获取学生选修的课程列表"""
    # 获取学生ID（从用户信息或其他方式获取）
    student_id = request.query_params.get('student_id')

    # 如果没有提供student_id，尝试从当前用户推断
    if not student_id:
        student_id = get_student_from_user(request.user)

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
