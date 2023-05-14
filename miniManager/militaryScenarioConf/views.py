
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

            military_organizations_data = json.loads(request.POST["military_org_data"])
            military_persons_data = json.loads(request.POST["military_person_data"])

            # verifica regras de hierarquia
            if len(military_organizations_data) > 0:
                for i in range(len(military_organizations_data) - 1):
                    org = military_organizations_data[i + 1]  # começa do segundo, pois o primeiro não tem comandante
                    type = org["type"]
                    type = MilitaryOrganizationPowerType.objects.get(name=type)  # Companhia
                    try:
                        type_commander = MilitaryOrganizationPowerType.objects.get(name=type.name).commander  # Batalhão
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
                        validate = True  # OK
                    else:
                        return HttpResponse("Commander type does not match. Organization creation failed.")

            try:
                last_scenario = MilitaryScenario.objects.latest('Id')
                scenario_id = last_scenario.Id + 1
            except:
                scenario_id = 1

            MilitaryScenario.objects.create(Id=scenario_id, name=scenario_name, description=scenario_description)
            scenario = MilitaryScenario.objects.get(Id=scenario_id)

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
        instances_output = ''

        #variáveis para armazenar os elementos do owl
        MilitaryScenario = ''
        CommDevices = []
        MilitaryOrganizations = []
        Operators = []
        Carriers = []
        Passanger = []
        guaranis = []
        MOPowertypes = []
        InterfPowertypes = []
        Interfaces = []


        #######

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
            class_names = ['MilitaryScenario', 'WirelessNetwork', 'CommDevice', 'CommDeviceOperator', 'Guarani', 'Interface', 'InterfacePowerType',
                           'MilitaryAsCarrier', 'MilitaryAsPassenger', 'MilitaryOrganization',
                           'MilitaryOrganizationPowerType']

            for i in range(len(list(ref_onto.classes()))):
                classe = list(ref_onto.classes())[i]
                if classe.name in class_names:
                    instances_output += f"\n\t<br><b>{classe.name}</b>:"
                    teste = classe.instances()
                    seen_names = set()  # Initialize an empty set to track seen names
                    for j in classe.instances():
                        if j.name not in seen_names:  # Check if the name is not already in the set
                            instances_output += f"<br>{j.name}"
                            seen_names.add(j.name)  # Add the name to the set to mark it as seen
                            #print(j.name)
                        if classe.name == 'MilitaryScenario':
                            MilitaryScenario = str(j.name)
                            MilitaryScenario_count = len(MilitaryScenario)
                        if classe.name == 'CommDevice':
                            CommDevices.append(str(j.name))
                            CommDevices_count = len(CommDevices)
                        if classe.name == 'Interface':
                            Interfaces.append(str(j.name))
                            Interfaces_count = len(Interfaces)
                        if classe.name == 'InterfacePowerType':
                            InterfPowertypes.append(str(j.name))
                            InterfPowertypes_count = len(InterfPowertypes)
                        if classe.name == 'MilitaryOrganizationPowerType':
                            MOPowertypes.append(str(j.name))
                            MOPowertypes_count = len(MOPowertypes)
                        if classe.name == 'MilitaryAsCarrier':
                            Carriers.append(str(j.name))
                            Carriers_count = len(Carriers)
                        if classe.name == 'CommDeviceOperator':
                            Operators.append(str(j.name))
                            Operators_count = len(Operators)
                        if classe.name == 'MilitaryOrganization':
                            MilitaryOrganizations.append(str(j.name))
                            MilitaryOrganizations_count = len(MilitaryOrganizations)
                        if classe.name == 'Guarani':
                            guaranis.append(str(j.name))
                            guaranis_count = len(guaranis)
                        if classe.name == 'MilitaryAsPassenger':
                            Passanger.append(str(j.name))
                            Passanger_count = len(Passanger)


                    instances_output += f"<hr>"

        context = {
            "types": types,
            "instances_output": instances_output
        }

        return render(request, 'upload_scenario.html', context)

