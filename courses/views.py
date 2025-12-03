from rest_framework import viewsets, filters
from rest_framework.response import Response
from .models import Course, StudentCourse  # Student pas ici, juste si tu veux récupérer ID
from .serializers import CourseSerializer, StudentCourseSerializer

# 🎯 Course CRUD + search (by name, instructor, category)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'instructor', 'category']  # recherche partielle

# 🔗 StudentCourse CRUD (association student-course)
class StudentCourseViewSet(viewsets.ModelViewSet):
    queryset = StudentCourse.objects.all()
    serializer_class = StudentCourseSerializer

    # ➕ Assign a student to a course
    def create(self, request, *args, **kwargs):
        student_id = request.data.get('student_id')
        course_id  = request.data.get('course_id')
        if not student_id or not course_id:
            return Response({'error': 'student_id and course_id are required'}, status=400)
        
        obj, created = StudentCourse.objects.get_or_create(student_id=student_id, course_id=course_id)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=201 if created else 200)
class StudentCourseViewSet(viewsets.ModelViewSet):
    queryset = StudentCourse.objects.all()
    serializer_class = StudentCourseSerializer