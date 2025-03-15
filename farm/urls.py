# urls.py
from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'farms', views.FarmViewSet, basename='farm')

farms_router = routers.NestedSimpleRouter(router, r'farms', lookup='farm')
farms_router.register(r'motors', views.MotorViewSet, basename='farm-motors')

motors_router = routers.NestedSimpleRouter(farms_router, r'motors', lookup='motor')
motors_router.register(r'valves', views.ValveViewSet, basename='motor-valves')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(farms_router.urls)),
    path('', include(motors_router.urls)),
]