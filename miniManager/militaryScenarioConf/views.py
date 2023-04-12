
from django.shortcuts import render
from django.views.generic import TemplateView
import json

import os

from owlready2 import *
import pprint

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
        types = MilitaryOrganizationPowerType.objects.all()

        if request.method == 'POST':
            scenario_name = request.POST["scenario_name"]
            scenario_description = request.POST["scenario_description"]

            military_organizations_data = json.loads(request.POST["military_org_data"])
            military_persons_data = json.loads(request.POST["military_person_data"])

            #create the scenario
            #MilitaryScenario.objects.create(name=scenario_name,description=scenario_description)

        context = {
            "types":types
        }

        return render(request, 'index.html', context)


class UploadScenarioView(TemplateView):
    template_name = 'upload_scenario.html'

    def upload_scenario(request):
        types = MilitaryOrganizationPowerType.objects.all()

        if request.method == 'POST':
            data = request.FILES['file']
            filename = data.name
            scenario_dir = os.path.join(os.path.dirname(__file__), 'scenarios')
            os.makedirs(scenario_dir, exist_ok=True)
            file_path = os.path.join(scenario_dir, filename)
            with open(file_path, 'wb+') as f:
                for chunk in data.chunks():
                    f.write(chunk)

            ref_onto = get_ontology(file_path).load()

            # read the ontology from the file
            #for c in ref_onto.classes():
            #    print(c)
            print("\n\t############### Printing OWL ###############")
            print("\nReference Ontology:\n", ref_onto)
            print("\nList of classes:\n", list(ref_onto.classes()))
            print("\nList of all properties:\n", list(ref_onto.properties()))
            print("\nList of object properties:\n", list(ref_onto.object_properties()))
            print("\nList of data properties:\n", list(ref_onto.data_properties()))

            print("\n\t############### Printing Instances ###############")

            for i in range(len(list(ref_onto.classes()))):
                classe = list(ref_onto.classes())[i]
                if (classe.instances()):
                    print(f"\n\t{classe.name}:")
                for j in classe.instances():
                    print(j.name)

        context = {
            "types": types
        }

        return render(request, 'upload_scenario.html', context)
