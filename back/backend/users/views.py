# users/views.py
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Teacher, Counselor
from .serializers import (
    UserSerializer, LoginSerializer, CreateUserSerializer,
    UpdateUserSerializer, ResetPasswordSerializer,
    TeacherSerializer, CounselorSerializer
)
from classes.models import Student
from classes.serializers import StudentListSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def login_view(request):
    """用户登录"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'code': 200,
                'message': '登录成功',
                'data': {
                    'user': user_data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            })
        return Response({
            'code': 401,
            'message': '用户名或密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)
    return Response({
        'code': 400,
        'message': '参数错误',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """用户登出"""
    logout(request)
    return Response({
        'code': 200,
        'message': '登出成功'
    })


@api_view(['GET'])
def current_user_view(request):
    """获取当前用户信息"""
    if request.user.is_authenticated:
        return Response({
            'code': 200,
            'data': UserSerializer(request.user).data
        })
    return Response({
        'code': 401,
        'message': '未登录'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def user_list_view(request):
    """获取用户列表 / 创建用户"""
    if request.method == 'GET':
        # 获取查询参数
        role = request.query_params.get('role')
        search = request.query_params.get('search')
        is_active = request.query_params.get('is_active')

        # 构建查询
        users = User.objects.all()

        if role:
            if role == 'admin':
                users = users.filter(is_superuser=True)
            else:
                users = users.filter(groups__name=role)

        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            users = users.filter(is_active=is_active_bool)

        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        total = users.count()

        users = users[start:end]
        serializer = UserSerializer(users, many=True)

        return Response({
            'code': 200,
            'data': {
                'results': serializer.data,
                'count': total,
                'page': page,
                'page_size': page_size
            }
        })

    elif request.method == 'POST':
        # 创建新用户
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'code': 200,
                'message': '用户创建成功',
                'data': UserSerializer(user).data
            })
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def user_detail_view(request, pk):
    """获取/更新/删除单个用户"""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({
            'code': 404,
            'message': '用户不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response({
            'code': 200,
            'data': serializer.data
        })

    elif request.method == 'PUT':
        serializer = UpdateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'code': 200,
                'message': '用户更新成功',
                'data': UserSerializer(user).data
            })
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response({
            'code': 200,
            'message': '用户删除成功'
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reset_password_view(request, pk):
    """重置用户密码"""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({
            'code': 404,
            'message': '用户不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({
            'code': 200,
            'message': '密码重置成功'
        })
    return Response({
        'code': 400,
        'message': '参数错误',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_user_status_view(request, pk):
    """切换用户状态（启用/禁用）"""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({
            'code': 404,
            'message': '用户不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    is_active = request.data.get('is_active')
    if is_active is not None:
        user.is_active = is_active
        user.save()
        return Response({
            'code': 200,
            'message': '用户已启用' if is_active else '用户已禁用',
            'data': {'is_active': user.is_active}
        })
    return Response({
        'code': 400,
        'message': '缺少is_active参数'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def teacher_profile_view(request):
    """获取当前登录教师的详细信息"""
    try:
        teacher = Teacher.objects.select_related('user').get(user=request.user)
        serializer = TeacherSerializer(teacher)
        return Response({
            'code': 200,
            'data': serializer.data
        })
    except Teacher.DoesNotExist:
        return Response({
            'code': 404,
            'message': '未找到教师信息'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def counselor_profile_view(request):
    """获取当前登录辅导员的详细信息"""
    try:
        counselor = Counselor.objects.select_related('user').get(user=request.user)
        serializer = CounselorSerializer(counselor)
        return Response({
            'code': 200,
            'data': serializer.data
        })
    except Counselor.DoesNotExist:
        return Response({
            'code': 404,
            'message': '未找到辅导员信息'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def teacher_list_view(request):
    """获取所有教师列表"""
    teachers = Teacher.objects.select_related('user').all()

    # 支持按院系筛选
    department = request.query_params.get('department')
    if department:
        teachers = teachers.filter(department__icontains=department)

    # 支持按姓名搜索
    search = request.query_params.get('search')
    if search:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(teacher_no__icontains=search)
        )

    serializer = TeacherSerializer(teachers, many=True)
    return Response({
        'code': 200,
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def counselor_list_view(request):
    """获取所有辅导员列表"""
    counselors = Counselor.objects.select_related('user').all()

    # 支持按院系筛选
    department = request.query_params.get('department')
    if department:
        counselors = counselors.filter(department__icontains=department)

    # 支持按姓名搜索
    search = request.query_params.get('search')
    if search:
        counselors = counselors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_no__icontains=search)
        )

    serializer = CounselorSerializer(counselors, many=True)
    return Response({
        'code': 200,
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def teacher_detail_view(request, pk):
    """获取指定教师的详细信息"""
    try:
        teacher = Teacher.objects.select_related('user').get(pk=pk)
        serializer = TeacherSerializer(teacher)
        return Response({
            'code': 200,
            'data': serializer.data
        })
    except Teacher.DoesNotExist:
        return Response({
            'code': 404,
            'message': '教师不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def counselor_detail_view(request, pk):
    """获取指定辅导员的详细信息"""
    try:
        counselor = Counselor.objects.select_related('user').get(pk=pk)
        serializer = CounselorSerializer(counselor)
        return Response({
            'code': 200,
            'data': serializer.data
        })
    except Counselor.DoesNotExist:
        return Response({
            'code': 404,
            'message': '辅导员不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_students_view(request):
    """搜索学生（用于干预记录创建时选择学生）

    支持按学号或姓名搜索，返回前10条结果
    """
    q = request.query_params.get('q', '')

    if len(q) < 2:
        return Response({
            'code': 400,
            'message': '搜索关键词至少需要2个字符'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 按学号或姓名搜索
    students = Student.objects.filter(
        Q(student_no__icontains=q) | Q(name__icontains=q)
    )[:10]

    serializer = StudentListSerializer(students, many=True)
    return Response({
        'code': 200,
        'message': '搜索成功',
        'data': serializer.data
    })


# ==================== 辅导员班级管理 ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def counselor_classes_view(request, pk):
    """获取辅导员管理的班级列表"""
    try:
        counselor = Counselor.objects.get(pk=pk)
        from classes.models import Class
        classes = Class.objects.filter(counselor_id=counselor.user_id)

        data = []
        for cls in classes:
            data.append({
                'id': cls.id,
                'name': cls.name,
                'grade': cls.grade,
                'student_count': cls.student_count,
                'major_name': None  # 简化处理，不从major_id查询
            })

        return Response({
            'code': 200,
            'data': data
        })
    except Counselor.DoesNotExist:
        return Response({
            'code': 404,
            'message': '辅导员不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_class_to_counselor_view(request, pk):
    """为辅导员分配班级"""
    try:
        counselor = Counselor.objects.get(pk=pk)
        class_ids = request.data.get('class_ids', [])

        if not class_ids:
            return Response({
                'code': 400,
                'message': '请选择要分配的班级'
            }, status=status.HTTP_400_BAD_REQUEST)

        from classes.models import Class
        assigned_count = 0
        for class_id in class_ids:
            try:
                cls = Class.objects.get(id=class_id)
                # 检查班级是否已被其他辅导员管理
                if cls.counselor_id and cls.counselor_id != counselor.user_id:
                    continue
                cls.counselor_id = counselor.user_id
                cls.save()
                assigned_count += 1
            except Class.DoesNotExist:
                continue

        return Response({
            'code': 200,
            'message': f'成功分配 {assigned_count} 个班级',
            'data': {'assigned_count': assigned_count}
        })
    except Counselor.DoesNotExist:
        return Response({
            'code': 404,
            'message': '辅导员不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def remove_class_from_counselor_view(request, pk):
    """解除辅导员与班级的关联"""
    try:
        counselor = Counselor.objects.get(pk=pk)
        class_id = request.data.get('class_id')

        if not class_id:
            return Response({
                'code': 400,
                'message': '请指定要解除的班级'
            }, status=status.HTTP_400_BAD_REQUEST)

        from classes.models import Class
        try:
            cls = Class.objects.get(id=class_id, counselor_id=counselor.user_id)
            cls.counselor_id = None
            cls.save()
            return Response({
                'code': 200,
                'message': '解除关联成功'
            })
        except Class.DoesNotExist:
            return Response({
                'code': 404,
                'message': '班级不存在或不属于该辅导员'
            }, status=status.HTTP_404_NOT_FOUND)
    except Counselor.DoesNotExist:
        return Response({
            'code': 404,
            'message': '辅导员不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_classes_view(request):
    """获取可分配的班级列表（未被管理的班级）"""
    from classes.models import Class
    # 获取所有未被管理的班级
    classes = Class.objects.filter(counselor_id__isnull=True)

    data = []
    for cls in classes:
        data.append({
            'id': cls.id,
            'name': cls.name,
            'grade': cls.grade,
            'student_count': cls.student_count
        })

    return Response({
        'code': 200,
        'data': data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def counselor_dashboard_stats_view(request):
    """获取辅导员Dashboard统计数据

    返回当前登录辅导员管理的班级和学生统计
    """
    user = request.user

    # 检查是否是辅导员
    is_counselor = False
    if hasattr(user, 'counselor_profile') and user.counselor_profile:
        is_counselor = True
    elif hasattr(user, 'groups'):
        is_counselor = user.groups.filter(name='counselor').exists()

    if not is_counselor:
        return Response({
            'code': 403,
            'message': '只有辅导员可以访问此接口'
        }, status=status.HTTP_403_FORBIDDEN)

    from classes.models import Class, Student

    # 获取辅导员管理的班级
    managed_classes = Class.objects.filter(counselor_id=user.id)
    class_ids = [c.id for c in managed_classes]

    # 统计班级信息
    class_stats = []
    total_students = 0
    for cls in managed_classes:
        # 统计该班级的学生数
        student_count = Student.objects.filter(class_id=cls.id).count()
        class_stats.append({
            'id': cls.id,
            'name': cls.name,
            'grade': cls.grade,
            'student_count': student_count
        })
        total_students += student_count

    # 获取管理的学生ID列表
    student_ids = []
    if class_ids:
        student_ids = list(Student.objects.filter(
            class_id__in=class_ids
        ).values_list('id', flat=True))

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total_students': total_students,
            'class_count': len(class_ids),
            'classes': class_stats,
            'student_ids': student_ids
        }
    })
