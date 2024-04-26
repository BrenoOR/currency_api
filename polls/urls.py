from django.urls import path
from . import views


app_name = "polls"
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:base_currency>/<str:target_currency>/latest_rate/', views.latest_rate, name='latest_rate'),
]
