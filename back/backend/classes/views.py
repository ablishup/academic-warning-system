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
    unassigned = request.query_params.get('unassigned')
    keyword = request.query_params.get('keyword')

    students = Student.objects.all()

    if unassigned == 'true':
        students = students.filter(class_id__isnull=True)
    elif class_id:
        students = students.filter(class_id=class_id)

    if keyword:
        students = students.filter(
            Q(name__icontains=keyword) |
            Q(student_no__icontains=keyword)
        )

    serializer = StudentListSerializer(students, many=True)
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


from users.models import User
from django.contrib.auth.models import User as AuthUser
from .models import Major


def _class_to_dict(cls):
    """将班级对象转为前端格式"""
    # 查找专业名称
    major_name = None
    try:
        major = Major.objects.get(id=cls.major_id) if cls.major_id else None
        major_name = major.name if major else None
    except Major.DoesNotExist:
        pass

    # 查找辅导员名称
    counselor_name = None
    try:
        counselor = AuthUser.objects.get(id=cls.counselor_id) if cls.counselor_id else None
        counselor_name = counselor.get_full_name() or counselor.username if counselor else None
    except AuthUser.DoesNotExist:
        pass

    # 统计预警人数（该班级下学生的活跃预警数）
    from warning_system.models import WarningRecord
    student_ids = Student.objects.filter(class_id=cls.id).values_list('id', flat=True)
    warning_count = WarningRecord.objects.filter(student_id__in=student_ids, status='active').count()

    return {
        'id': cls.id,
        'name': cls.name,
        'grade': cls.grade,
        'major': major_name or '',
        'major_id': cls.major_id,
        'counselor_id': cls.counselor_id,
        'counselor_name': counselor_name or '',
        'student_count': Student.objects.filter(class_id=cls.id).count(),
        'warning_count': warning_count,
        'created_at': cls.created_at,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def class_list_view(request):
    """获取班级列表 / 创建班级"""
    if request.method == 'GET':
        classes = Class.objects.all()
        data = [_class_to_dict(c) for c in classes]
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': data
        })
    elif request.method == 'POST':
        data = request.data
        try:
            cls = Class.objects.create(
                name=data.get('name', ''),
                grade=data.get('grade', ''),
                major_id=data.get('major_id'),
                counselor_id=data.get('counselor_id'),
            )
            return Response({
                'code': 200,
                'message': '创建成功',
                'data': _class_to_dict(cls)
            })
        except Exception as e:
            return Response({
                'code': 400,
                'message': f'创建失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def class_detail_view(request, pk):
    """班级详情 / 更新 / 删除"""
    try:
        cls = Class.objects.get(pk=pk)
    except Class.DoesNotExist:
        return Response({
            'code': 404,
            'message': '班级不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': _class_to_dict(cls)
        })
    elif request.method in ('PUT', 'PATCH'):
        data = request.data
        cls.name = data.get('name', cls.name)
        cls.grade = data.get('grade', cls.grade)
        cls.major_id = data.get('major_id', cls.major_id)
        cls.counselor_id = data.get('counselor_id', cls.counselor_id)
        cls.save()
        return Response({
            'code': 200,
            'message': '更新成功',
            'data': _class_to_dict(cls)
        })
    elif request.method == 'DELETE':
        cls.delete()
        return Response({
            'code': 200,
            'message': '删除成功'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def class_students_view(request, class_id):
    """获取班级学生列表"""
    students = Student.objects.filter(class_id=class_id)
    from warning_system.models import WarningRecord
    data = []
    for s in students:
        warning_count = WarningRecord.objects.filter(student_id=s.id, status='active').count()
        data.append({
            'id': s.id,
            'student_no': s.student_no,
            'name': s.name,
            'gender': s.gender,
            'phone': s.phone or '',
            'warning_count': warning_count,
        })
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def class_add_students_view(request, class_id):
    """批量添加学生到班级"""
    student_ids = request.data.get('student_ids', [])
    if not student_ids:
        return Response({
            'code': 400,
            'message': '请选择要添加的学生'
        }, status=status.HTTP_400_BAD_REQUEST)

    updated = 0
    for sid in student_ids:
        try:
            student = Student.objects.get(id=sid)
            student.class_id = class_id
            student.save()
            updated += 1
        except Student.DoesNotExist:
            continue

    return Response({
        'code': 200,
        'message': f'成功添加 {updated} 名学生',
        'data': {'updated_count': updated}
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def class_remove_student_view(request, class_id):
    """从班级移除学生"""
    student_id = request.data.get('student_id')
    if not student_id:
        return Response({
            'code': 400,
            'message': '请指定学生'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        student = Student.objects.get(id=student_id, class_id=class_id)
        student.class_id = None
        student.save()
        return Response({
            'code': 200,
            'message': '移除成功'
        })
    except Student.DoesNotExist:
        return Response({
            'code': 404,
            'message': '学生不存在或不属于该班级'
        }, status=status.HTTP_404_NOT_FOUND)


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def major_list_view(request):
    """获取专业列表"""
    majors = Major.objects.all()
    data = [{'id': m.id, 'name': m.name} for m in majors]
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': data
    })
