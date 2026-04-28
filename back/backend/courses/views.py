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
from users.utils import get_student_from_user


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
        # 查找users表中对应的用户ID（外键约束引用users表而非auth_user）
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT id FROM users WHERE username = %s', [self.request.user.username])
            result = cursor.fetchone()
            user_id_in_users = result[0] if result else None
        serializer.save(created_by_id=user_id_in_users)

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


# 状态映射
COURSE_STATUS_MAP = {
    'active': 1,
    'pending': 0,
    'ended': 2,
}
COURSE_STATUS_REVERSE = {v: k for k, v in COURSE_STATUS_MAP.items()}


def _course_to_dict(course):
    """将课程对象转为前端格式"""
    return {
        'id': course.id,
        'name': course.name,
        'code': course.course_no,
        'description': course.description,
        'credit': float(course.credit) if course.credit else 0,
        'hours': course.hours,
        'teacher_id': course.teacher_id,
        'semester': course.semester,
        'status': COURSE_STATUS_REVERSE.get(course.status, 'active'),
        'student_count': CourseEnrollment.objects.filter(course_id=course.id).count(),
        'created_at': course.created_at,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def course_list_view(request):
    """获取课程列表 / 创建课程"""
    if request.method == 'GET':
        courses = Course.objects.all()
        data = [_course_to_dict(c) for c in courses]
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': data
        })
    elif request.method == 'POST':
        data = request.data
        try:
            course = Course.objects.create(
                course_no=data.get('code', ''),
                name=data.get('name', ''),
                description=data.get('description', ''),
                credit=data.get('credit', 2.0),
                hours=data.get('hours', 48),
                teacher_id=data.get('teacher_id'),
                semester=data.get('semester', ''),
                status=COURSE_STATUS_MAP.get(data.get('status'), 1),
            )
            return Response({
                'code': 200,
                'message': '创建成功',
                'data': _course_to_dict(course)
            })
        except Exception as e:
            return Response({
                'code': 400,
                'message': f'创建失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def course_detail_view(request, pk):
    """课程详情 / 更新 / 删除"""
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({
            'code': 404,
            'message': '课程不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': _course_to_dict(course)
        })
    elif request.method in ('PUT', 'PATCH'):
        data = request.data
        course.course_no = data.get('code', course.course_no)
        course.name = data.get('name', course.name)
        course.description = data.get('description', course.description)
        course.credit = data.get('credit', course.credit)
        course.hours = data.get('hours', course.hours)
        course.teacher_id = data.get('teacher_id', course.teacher_id)
        course.semester = data.get('semester', course.semester)
        if 'status' in data:
            course.status = COURSE_STATUS_MAP.get(data['status'], course.status)
        course.save()
        return Response({
            'code': 200,
            'message': '更新成功',
            'data': _course_to_dict(course)
        })
    elif request.method == 'DELETE':
        course.delete()
        return Response({
            'code': 200,
            'message': '删除成功'
        })


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_students_view(request, course_id):
    """获取课程学生列表"""
    from classes.models import Student
    enrollments = CourseEnrollment.objects.filter(course_id=course_id)
    student_ids = [e.student_id for e in enrollments]
    students = Student.objects.filter(id__in=student_ids)
    data = []
    for s in students:
        data.append({
            'id': s.id,
            'student_no': s.student_no,
            'name': s.name,
            'gender': s.gender,
            'phone': s.phone or '',
        })
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def course_add_students_view(request, course_id):
    """批量添加学生到课程"""
    student_ids = request.data.get('student_ids', [])
    if not student_ids:
        return Response({
            'code': 400,
            'message': '请选择要添加的学生'
        }, status=status.HTTP_400_BAD_REQUEST)

    created = 0
    for sid in student_ids:
        if not CourseEnrollment.objects.filter(student_id=sid, course_id=course_id).exists():
            CourseEnrollment.objects.create(student_id=sid, course_id=course_id)
            created += 1

    return Response({
        'code': 200,
        'message': f'成功添加 {created} 名学生',
        'data': {'created_count': created}
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def course_remove_student_view(request, course_id):
    """从课程移除学生"""
    student_id = request.data.get('student_id')
    if not student_id:
        return Response({
            'code': 400,
            'message': '请指定学生'
        }, status=status.HTTP_400_BAD_REQUEST)

    deleted, _ = CourseEnrollment.objects.filter(student_id=student_id, course_id=course_id).delete()
    if deleted:
        return Response({
            'code': 200,
            'message': '移除成功'
        })
    return Response({
        'code': 404,
        'message': '该学生未选修此课程'
    }, status=status.HTTP_404_NOT_FOUND)
