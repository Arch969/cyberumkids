from django.urls import path
from . import views
urlpatterns = [
  path('', views.login_view, name='login'),
  path('logout/', views.logout_view, name='logout'),
  path('courses/', views.courses_index, name='courses_index'),
  path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
  path('api/v1/courses/', views.api_courses),
  path('api/v1/courses/<slug:slug>/lessons/', views.api_course_lessons),
  path('cabinet/', views.cabinet_view, name='cabinet'),
  # простая «начислялка» звёзд для демо
  path('earn-stars/', views.earn_stars, name='earn_stars'),

  # API (опционально, для динамики на JS)
  path('api/v1/me/', views.api_me, name='api_me'),

  path('dialogue/<slug:slug>/', views.dialogue_scene, name='dialogue_scene'),

  path('api/v1/teacher/students/', views.api_teacher_students, name='api_teacher_students'),

  path('calendar/', views.calendar_view, name='calendar'),
  path('api/v1/my-schedule/', views.api_my_schedule, name='api_my_schedule'),
  path("scratch/map/", views.scratch_map, name="scratch_map"),
]
