from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='interface_index'),
    path('<str:interface_name>/', views.InterfaceView.as_view(), name='interface'),
]
