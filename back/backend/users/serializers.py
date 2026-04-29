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
        # 从关联扩展表按角色读取工号/学号
        role = self.get_role(obj)
        try:
            if role == 'teacher' and hasattr(obj, 'teacher_profile'):
                return obj.teacher_profile.teacher_no or ''
            elif role == 'counselor' and hasattr(obj, 'counselor_profile'):
                return obj.counselor_profile.employee_no or ''
            elif role == 'student' and hasattr(obj, 'profile'):
                return obj.profile.employee_no or ''
        except Exception:
            pass
        return ''

    def get_phone(self, obj):
        role = self.get_role(obj)
        try:
            if role == 'teacher' and hasattr(obj, 'teacher_profile'):
                return obj.teacher_profile.phone or ''
            elif role == 'counselor' and hasattr(obj, 'counselor_profile'):
                return obj.counselor_profile.phone or ''
            elif role == 'student' and hasattr(obj, 'profile'):
                return obj.profile.phone or ''
        except Exception:
            pass
        return ''


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

        # 根据角色设置权限和分组，并同步创建扩展表记录
        from users.models import UserProfile
        if role == 'teacher':
            Teacher.objects.create(
                user=user,
                teacher_no=student_no or '',
                phone=phone or ''
            )
        elif role == 'counselor':
            Counselor.objects.create(
                user=user,
                employee_no=student_no or '',
                phone=phone or ''
            )
        elif role == 'student':
            UserProfile.objects.create(
                user=user,
                employee_no=student_no or '',
                phone=phone or ''
            )

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
    student_no = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email',
                  'role', 'student_no', 'phone', 'is_active']

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password', None)
        student_no = validated_data.pop('student_no', None)
        phone = validated_data.pop('phone', None)

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

        # 同步更新扩展表
        from users.models import UserProfile
        current_role = None
        if role:
            current_role = role
        else:
            if instance.is_superuser:
                current_role = 'admin'
            elif instance.groups.filter(name='teacher').exists():
                current_role = 'teacher'
            elif instance.groups.filter(name='counselor').exists():
                current_role = 'counselor'
            else:
                current_role = 'student'

        if current_role == 'teacher':
            profile, _ = Teacher.objects.get_or_create(user=instance)
            if student_no is not None:
                profile.teacher_no = student_no
            if phone is not None:
                profile.phone = phone
            profile.save()
        elif current_role == 'counselor':
            profile, _ = Counselor.objects.get_or_create(user=instance)
            if student_no is not None:
                profile.employee_no = student_no
            if phone is not None:
                profile.phone = phone
            profile.save()
        elif current_role == 'student':
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            if student_no is not None:
                profile.employee_no = student_no
            if phone is not None:
                profile.phone = phone
            profile.save()

        return instance


class ResetPasswordSerializer(serializers.Serializer):
    """重置密码序列化器"""
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)


class TeacherSerializer(serializers.ModelSerializer):
    """教师信息序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.first_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user_id', 'username', 'name', 'email', 'teacher_no',
                  'department', 'title', 'phone', 'office', 'is_active', 'date_joined',
                  'created_at', 'updated_at']


class CounselorSerializer(serializers.ModelSerializer):
    """辅导员信息序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.first_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)

    class Meta:
        model = Counselor
        fields = ['id', 'user_id', 'username', 'name', 'email', 'employee_no',
                  'department', 'phone', 'office', 'is_active',
                  'created_at', 'updated_at']
