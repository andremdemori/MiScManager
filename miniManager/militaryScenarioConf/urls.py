from django.urls import path
from .views import HomeScenarioView



urlpatterns = [
    path('index/', HomeScenarioView.homescenario, name='home_scenario'),
#    path('page1/', TestPlanView.as_view(), name='test-plan'),
#    path('test-plans/', TestPlansView.as_view(), name='test-plans')
]