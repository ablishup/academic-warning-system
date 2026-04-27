from classes.models import Student, Class


def get_counselor_student_ids(user):
    """获取辅导员管理班级的所有学生ID"""
    managed_classes = Class.objects.filter(counselor_id=user.id)
    class_ids = [c.id for c in managed_classes]
    if not class_ids:
        return []
    return list(Student.objects.filter(class_id__in=class_ids).values_list('id', flat=True))
