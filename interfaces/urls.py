from django.urls import path
from . import views

urlpatterns = [
    path('<str:interface_name>/', views.InterfaceView.as_view(), name='interface'),
]
