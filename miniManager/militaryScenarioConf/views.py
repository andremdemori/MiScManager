
from django.shortcuts import render
from django.views.generic import TemplateView
import json

import os

from owlready2 import *
import pprint

from .models import *

# Create your views here.

from django.http import JsonResponse, HttpResponse
from .models import MilitaryOrganizationPowerType
from militaryScenarioConf.models import *

def fetch_power_types(request):
    power_types = MilitaryOrganizationPowerType.objects.values_list('name', flat=True)
    return JsonResponse({"power_types": list(power_types)})

class HomeScenarioView(TemplateView):
    template_name = 'index.html'
    def homescenario(request):
        types = MilitaryOrganizationPowerType.objects.all()

        if request.method == 'POST':

            ###CRIA O CENÁRIO
            scenario_name = request.POST["scenario_name"]
            scenario_description = request.POST["scenario_description"]
            scenario_id = 0
            validate = False
            commander_type = ''
            type_commander = ''

            try:
                last_scenario = MilitaryScenario.objects.latest('Id')
                scenario_id = last_scenario.Id + 1
            except:
                scenario_id = 1

            MilitaryScenario.objects.create(Id=scenario_id, name=scenario_name, description=scenario_description)
            scenario = MilitaryScenario.objects.get(Id=scenario_id)

            military_organizations_data = json.loads(request.POST["military_org_data"])
            military_persons_data = json.loads(request.POST["military_person_data"])


            # verifica regras de hierarquia
            if len(military_organizations_data) > 0:
                for i in range(len(military_organizations_data)-1):
                    org = military_organizations_data[i+1]
                    type = org["type"]
                    type = MilitaryOrganizationPowerType.objects.get(name=type) # Companhia
                    try:
                        type_commander = MilitaryOrganizationPowerType.objects.get(name=type.name).commander # Batalhão
                    except:
                        type_commander = None
                    name = org["mo_name"]
                    commander = org["commander"]
                    if commander == "":
                        commander = None
                    else:
                        for orga in military_organizations_data:
                            if orga.get('mo_name') == commander:
                                commander_type = orga.get('type')
                                commander_type = MilitaryOrganizationPowerType.objects.get(name=commander_type)
                    if type != commander_type and commander_type == type_commander:
                        validate = True # OK
                    else:
                        #MilitaryScenario.objects.get(Id=scenario_id).delete()
                        return HttpResponse("Commander type does not match. Organization creation failed.")

            ###CRIA MILITARY ORGANIZATIONS, MILITARY PERSONS E CARRIES

            ###CRIA MILITARY ORGANIZATIONS
            if len(military_organizations_data) > 0:
                for i in range(len(military_organizations_data)):
                    org = military_organizations_data[i]

                    type = org["type"]
                    type = MilitaryOrganizationPowerType.objects.get(name=type)
                    name = org["mo_name"]
                    commander = org["commander"]
                    if commander == "":
                        commander = None
                    else:
                        commander = MilitaryOrganization.objects.get(name=commander,scenario=scenario)

                    MilitaryOrganization.objects.create(type=type,name=name,commander=commander,scenario=scenario)


            ###CRIA MILITARY PERSONS
            if len(military_persons_data) > 0:
                for i in range(len(military_persons_data)):
                    person = military_persons_data[i]

                    identifier = person["identifier"]
                    mo = person["person_mo"]
                    mo = MilitaryOrganization.objects.get(name=mo,scenario=scenario)
                    carrier = person["carrier"]
                    if carrier == 'Guarani':
                        last_guarani = Guarani.objects.latest('Id')
                        Id = last_guarani.Id + 1
                        last_guarani_name = last_guarani.name
                        number = last_guarani_name[7:] # remove first 7 characters ("guarani") from the string
                        number = int(number)
                        number = number + 1
                        number = str(number)
                        new_guarani_name = 'guarani'+number
                        Guarani.objects.create(Id=Id,VisibilityRange=1000,v_min=3.5,v_max=95,scenario=scenario,
                                               category='Armored',Military_Organization=mo,name=new_guarani_name)
                        carrier = Carrier.objects.latest('Id')
                    elif carrier == 'By Foot':
                        carrier = Carrier.objects.get(Id=1) # BY FOOT
                    MilitaryPerson.objects.create(Identifier=identifier,Military_Organization=mo,CommDevice_Carrier=carrier,scenario=scenario)

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
