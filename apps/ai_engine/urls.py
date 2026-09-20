from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    # Forecast generation & history
    path('forecast/<str:symbol>/', views.GenerateForecastView.as_view(), name='generate_forecast'),
    path('history/', views.PredictionHistoryView.as_view(), name='prediction_history'),
    
    # Accuracy audits, Scenario simulator, Physical Gold, and Full Data Refresh
    path('full-refresh/', views.FullDataRefreshView.as_view(), name='full_data_refresh'),
    path('accuracy-audit/', views.AccuracyAuditView.as_view(), name='accuracy_audit'),
    path('simulate-scenario/', views.ScenarioSimulatorView.as_view(), name='simulate_scenario'),
    path('physical-gold/', views.PhysicalGoldPredictionView.as_view(), name='physical_gold'),
    path('physical-gold-chart/', views.PhysicalGoldChartView.as_view(), name='physical_gold_chart'),
]


