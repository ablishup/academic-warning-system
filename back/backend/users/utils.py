from classes.models import Student, Class


def get_counselor_student_ids(user):
    """获取辅导员管理班级的所有学生ID"""
    managed_classes = Class.objects.filter(counselor_id=user.id)
    class_ids = [c.id for c in managed_classes]
    if not class_ids:
        return []
    return list(Student.objects.filter(class_id__in=class_ids).values_list('id', flat=True))


def get_student_from_user(user):
    """从当前登录用户获取学生ID（多策略匹配）"""
    if not user or not user.is_authenticated:
        return None

    # 方法1: username 匹配学号
    student = Student.objects.filter(student_no=user.username).first()
    if student:
        return student.id

    # 方法2: first_name 匹配姓名
    if user.first_name:
        student = Student.objects.filter(name=user.first_name).first()
        if student:
            return student.id

    # 方法3: 兼容旧账号（student_N）
    if user.username.startswith('student_'):
        try:
            sid = int(user.username.split('_')[1])
            if Student.objects.filter(id=sid).exists():
                return sid
        except (ValueError, IndexError):
            pass

    # 方法4: profile 关联
    try:
        profile = getattr(user, 'profile', None)
        if profile and hasattr(profile, 'employee_no') and profile.employee_no:
            student = Student.objects.filter(student_no=profile.employee_no).first()
            if student:
                return student.id
    except Exception:
        pass

    return None
