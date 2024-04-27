from django.urls import path
from . import views

app_name = "exchange_rates"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:base_currency>/<str:target_currency>/latest_rate/', views.LatestRateView.as_view(), name='latest_rate'),
    path('<str:base_currency>/<str:target_currency>/historical_data/', views.HistoricalDataView.as_view(),
         name='historical_data'),
]
