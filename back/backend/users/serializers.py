# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'role']

    def get_role(self, obj):
        # 根据用户名或其他规则推断角色
        if obj.is_superuser:
            return 'admin'
        elif obj.groups.filter(name='teacher').exists():
            return 'teacher'
        elif obj.groups.filter(name='counselor').exists():
            return 'counselor'
        return 'student'


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
