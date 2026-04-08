# users/views.py
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .serializers import UserSerializer, LoginSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """用户登录"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'code': 200,
                'message': '登录成功',
                'data': UserSerializer(user).data
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


@api_view(['GET'])
def user_list_view(request):
    """获取用户列表（管理员功能）"""
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response({
        'code': 200,
        'data': serializer.data
    })
