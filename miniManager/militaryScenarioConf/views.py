
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from .models import *

# Create your views here.

from django.http import JsonResponse
from .models import MilitaryOrganizationPowerType

def fetch_power_types(request):
    power_types = MilitaryOrganizationPowerType.objects.values_list('name', flat=True)
    return JsonResponse({"power_types": list(power_types)})

class HomeScenarioView(TemplateView):
    template_name = 'index.html'

    def homescenario(request):
        if request.method == 'POST':
            scenario_name = request.POST["scenario_name"]
            scenario_description = request.POST["scenario_description"]

            military_organizations_data = json.loads(request.POST["military_organizations"])
            military_persons_data = json.loads(request.POST["military_persons"])

            #create the scenario
            MilitaryScenario.objects.create(name=scenario_name,description=scenario_description)

            #create om


        return render(request, 'index.html')
