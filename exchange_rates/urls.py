from django.urls import path
from . import views

app_name = 'exchange_rates'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:base_currency>/<str:target_currency>/<str:value>', views.ExchangeRateView.as_view(),
         name='exchange_rate'),
    path('<str:base_currency>/<str:target_currency>/<str:value>/calc', views.calc_exchange, name='calc_exchange'),
    path('latest_rate/<str:base_currency>/<str:target_currency>/', views.LatestRateView.as_view(), name='latest_rate'),
    path('<str:base_currency>/<str:target_currency>/historical_data/<str:start_date>/<str:end_date>',
         views.HistoricalDataView.as_view(),
         name='historical_data'),
    path('<str:base_currency>/<str:target_currency>/historical_data/setup', views.set_history, name='change_range'),
    path('historical_data/<str:base_currency>/<str:target_currency>/<str:start_date>/<str:end_date>',
         views.HistoricalDataJSView.as_view(), name='historical_data_js'),
]
