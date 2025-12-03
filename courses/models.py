from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=255)
    instructor = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    schedule = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class StudentCourse(models.Model):
    student_id = models.BigIntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student_id', 'course')

    def __str__(self):
        return f"Student {self.student_id} -> Course {self.course.name}"