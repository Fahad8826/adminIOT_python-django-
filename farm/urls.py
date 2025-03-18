from django.urls import path


from .views import (
    FarmListCreateView, FarmDetailView,
    MotorListCreateView, MotorDetailView,
    ValveListCreateView, ValveDetailView, farm_management
)

urlpatterns = [
    path('farmlist/', FarmListCreateView.as_view(), name='farm-list'),
    path('farms/<int:pk>/', FarmDetailView.as_view(), name='farm-detail'),

    path('farms/<int:farm_id>/motors/', MotorListCreateView.as_view(), name='motor-list'),
    path('farms/<int:farm_id>/motors/<int:pk>/', MotorDetailView.as_view(), name='motor-detail'),

    path('farms/<int:farm_id>/motors/<int:motor_id>/valves/', ValveListCreateView.as_view(), name='valve-list'),
    path('farms/<int:farm_id>/motors/<int:motor_id>/valves/<int:pk>/', ValveDetailView.as_view(), name='valve-detail'),


    path('farm-html-CRUD/', farm_management, name='farm-management'),
]
