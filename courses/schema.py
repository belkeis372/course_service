# courses/schema.py
import graphene
from graphene_django import DjangoObjectType
from .models import Course, StudentCourse
import requests

# 🔹 تعريف أنواع GraphQL
class CourseType(DjangoObjectType):
    class Meta:
        model = Course
        fields = "__all__"

class StudentCourseType(DjangoObjectType):
    class Meta:
        model = StudentCourse
        fields = "__all__"

# 🔹 نوع Student (يأتي من خدمة الطلاب)
class StudentType(graphene.ObjectType):
    id = graphene.Int()
    firstName = graphene.String()
    lastName = graphene.String()
    email = graphene.String()

# 🔹 نوع مخصص يجمع Student مع Courses
class StudentWithCoursesType(graphene.ObjectType):
    student = graphene.Field(StudentType)
    courses = graphene.List(CourseType)

# 🔹 الاستعلامات الرئيسية
class Query(graphene.ObjectType):
    
    # 🔍 جلب جميع الكورسات
    all_courses = graphene.List(CourseType)
    
    # 🔍 جلب كورسات طالب معين
    student_courses = graphene.List(CourseType, student_id=graphene.Int(required=True))
    
    # 🔍 جلب طالب مع كورساته (الربط الرئيسي)
    get_student_with_courses = graphene.Field(StudentWithCoursesType, student_id=graphene.Int(required=True))
    
    # 🔍 جلب جميع الطلاب مع كورساتهم
    all_students_with_courses = graphene.List(StudentWithCoursesType)

    def resolve_all_courses(self, info):
        return Course.objects.all()

    def resolve_student_courses(self, info, student_id):
        # جلب كورسات الطالب من جدول StudentCourse
        student_courses = StudentCourse.objects.filter(student_id=student_id)
        course_ids = [sc.course.id for sc in student_courses]
        return Course.objects.filter(id__in=course_ids)

    def resolve_get_student_with_courses(self, info, student_id):
        try:
            # 📡 جلب بيانات الطالب من خدمة الطلاب (Spring Boot)
            student_response = requests.get(f'http://localhost:8081/api/students/{student_id}')
            
            if student_response.status_code == 200:
                student_data = student_response.json()
                
                # 🔍 جلب كورسات الطالب من قاعدة البيانات المحلية
                student_courses = StudentCourse.objects.filter(student_id=student_id)
                course_ids = [sc.course.id for sc in student_courses]
                courses = Course.objects.filter(id__in=course_ids)
                
                # إنشاء كائن Student
                student = StudentType(
                    id=student_data['id'],
                    firstName=student_data['firstName'],
                    lastName=student_data['lastName'],
                    email=student_data['email']
                )
                
                return StudentWithCoursesType(
                    student=student,
                    courses=courses
                )
            else:
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None

    def resolve_all_students_with_courses(self, info):
        try:
            # 📡 جلب جميع الطلاب من خدمة الطلاب
            students_response = requests.get('http://localhost:8081/api/students/all')
            
            if students_response.status_code == 200:
                students_data = students_response.json()
                results = []
                
                for student_data in students_data:
                    # 🔍 جلب كورسات كل طالب
                    student_courses = StudentCourse.objects.filter(student_id=student_data['id'])
                    course_ids = [sc.course.id for sc in student_courses]
                    courses = Course.objects.filter(id__in=course_ids)
                    
                    # إنشاء كائن Student
                    student = StudentType(
                        id=student_data['id'],
                        firstName=student_data['firstName'],
                        lastName=student_data['lastName'],
                        email=student_data['email']
                    )
                    
                    results.append(StudentWithCoursesType(
                        student=student,
                        courses=courses
                    ))
                
                return results
            else:
                return []
                
        except Exception as e:
            print(f"Error: {e}")
            return []

# 🔹 طفرات لإضافة علاقات
class AssignStudentToCourse(graphene.Mutation):
    class Arguments:
        student_id = graphene.Int(required=True)
        course_id = graphene.Int(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, student_id, course_id):
        try:
            # التحقق من وجود الطالب في الخدمة الأخرى
            student_response = requests.get(f'http://localhost:8081/api/students/{student_id}')
            if student_response.status_code != 200:
                return AssignStudentToCourse(success=False, message="Student not found")
            
            # التحقق من وجود الكورس محلياً
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return AssignStudentToCourse(success=False, message="Course not found")
            
            # إنشاء العلاقة في جدول StudentCourse
            student_course, created = StudentCourse.objects.get_or_create(
                student_id=student_id,
                course=course
            )
            
            message = "Student assigned to course" if created else "Student already in course"
            return AssignStudentToCourse(success=True, message=message)
            
        except Exception as e:
            return AssignStudentToCourse(success=False, message=str(e))

class Mutation(graphene.ObjectType):
    assign_student_to_course = AssignStudentToCourse.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)