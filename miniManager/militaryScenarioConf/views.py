
from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class HomeScenarioView(TemplateView):
    template_name = 'index.html'

    def homescenario(request):
        if request.method == 'POST':
            scenario_name = request.POST.get('scenario_name')
            scenario_description = request.POST.get('scenario_description')
        return render(request, 'index.html')
