# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from .models import Teacher, Counselor


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    role = serializers.SerializerMethodField()
    student_no = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff',
                  'is_active', 'role', 'student_no', 'phone', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def get_role(self, obj):
        # 根据用户组推断角色
        if obj.is_superuser:
            return 'admin'
        elif obj.groups.filter(name='teacher').exists():
            return 'teacher'
        elif obj.groups.filter(name='counselor').exists():
            return 'counselor'
        return 'student'

    def get_student_no(self, obj):
        # 从profile或额外字段获取学号/工号
        return getattr(obj, 'student_no', '')

    def get_phone(self, obj):
        return getattr(obj, 'phone', '')


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class CreateUserSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    role = serializers.ChoiceField(
        choices=['student', 'teacher', 'counselor', 'admin'],
        required=True
    )
    student_no = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email',
                  'role', 'student_no', 'phone', 'is_active']

    def create(self, validated_data):
        role = validated_data.pop('role')
        student_no = validated_data.pop('student_no', '')
        phone = validated_data.pop('phone', '')

        # 创建用户
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            is_active=validated_data.get('is_active', True)
        )

        # 设置额外字段（需要扩展User模型或使用Profile）
        # 这里先存储在user的自定义属性中
        if student_no:
            # 将学号/工号存储在last_name中，或使用自定义字段
            pass

        # 根据角色设置权限和分组
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
        else:
            # 添加到对应用户组
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)

        return user

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password', None)

        # 更新基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 更新密码
        if password:
            instance.set_password(password)

        instance.save()

        # 更新角色
        if role:
            # 清除原有组
            instance.groups.clear()
            if role == 'admin':
                instance.is_staff = True
                instance.is_superuser = True
            else:
                instance.is_staff = False
                instance.is_superuser = False
                group, _ = Group.objects.get_or_create(name=role)
                instance.groups.add(group)
            instance.save()

        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    """更新用户序列化器（不强制要求密码）"""
    password = serializers.CharField(write_only=True, required=False, min_length=6)
    role = serializers.ChoiceField(
        choices=['student', 'teacher', 'counselor', 'admin'],
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email',
                  'role', 'is_active']

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password', None)

        # 更新基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 更新密码（如果提供）
        if password:
            instance.set_password(password)

        instance.save()

        # 更新角色
        if role:
            instance.groups.clear()
            if role == 'admin':
                instance.is_staff = True
                instance.is_superuser = True
            else:
                instance.is_staff = False
                instance.is_superuser = False
                group, _ = Group.objects.get_or_create(name=role)
                instance.groups.add(group)
            instance.save()

        return instance


class ResetPasswordSerializer(serializers.Serializer):
    """重置密码序列化器"""
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)


class TeacherSerializer(serializers.ModelSerializer):
    """教师信息序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.first_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user_id', 'username', 'name', 'email', 'teacher_no',
                  'department', 'title', 'phone', 'office', 'created_at', 'updated_at']


class CounselorSerializer(serializers.ModelSerializer):
    """辅导员信息序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.first_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Counselor
        fields = ['id', 'user_id', 'username', 'name', 'email', 'employee_no',
                  'department', 'phone', 'office', 'created_at', 'updated_at']
