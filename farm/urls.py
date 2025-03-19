# urls.py
from django.urls import path
from .views import FarmListCreateView, FarmDetailView, create_farm_page

urlpatterns = [
    path('farms/', FarmListCreateView.as_view(), name='farm-list-create'),
    path('farms/<int:pk>/', FarmDetailView.as_view(), name='farm-detail'),

    path('create-farm/', create_farm_page, name='create_farm_page'),
]