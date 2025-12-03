from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, StudentCourseViewSet

# Création du router pour gérer automatiquement les endpoints CRUD
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'student-courses', StudentCourseViewSet, basename='studentcourse')

urlpatterns = [
    path('', include(router.urls)),
]

# في urls.py لخدمة Course

from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # ... الروابط الحالية لـ REST API
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]