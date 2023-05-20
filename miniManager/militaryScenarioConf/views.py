
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
        scenario_name = ''
        latest_scenario = ''
        MO_dictionary = {}
        commander_name = ''
        MP_dictionary = {}
        guaranis = []

        CommDevices = []
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

                    seen_names = set()  # Initialize an empty set to store the seen names
                    for j in classe.instances():
                        if j.name not in seen_names:  # Check if the name is not already in the set
                            instances_output += f"<br>{j.name}"
                            seen_names.add(j.name)  # Add the name to the set of seen names
                    instances_output += f"<hr>"

            for ind in ref_onto.classes():  # for each individual

                seen_names = set()
                classe_ = str(ind).split(".")[-1]

                ### COLETA INFORMAÇÕES PARA CRIAÇÃO DO CENÁRIO (PROPERTIES)###

                if classe_ == 'MilitaryScenario':
                    for j in ind.instances():

                        scenario_name = str(j.name)
                        #print(f"\n{j.name}")

                if classe_ == 'MilitaryOrganization':
                    for j in ind.instances():
                        if j.name not in seen_names:
                            MO_dictionary[j.name] = {}
                            seen_names.add(j.name)
                            for p in j.get_properties():
                                p_value = str(p._get_value_for_individual(j)).split(".")[-1]
                                MO_dictionary[j.name][p.name] = p_value

                    # Find the element without 'isSubordinateTo'
                    element_without_subordinate = None
                    for key, value in MO_dictionary.items():
                        if 'isSubordinateTo' not in value:
                            element_without_subordinate = (key, value)
                            break

                    # Remove the element without 'isSubordinateTo' from the dictionary
                    if element_without_subordinate is not None:
                        key, value = element_without_subordinate
                        del MO_dictionary[key]

                    # Insert the element without 'isSubordinateTo' as the first element in the dictionary
                    if element_without_subordinate is not None:
                        updated_data = {key: value}
                        updated_data.update(MO_dictionary)
                        MO_dictionary = updated_data

                if classe_ == 'Ue':
                    for j in ind.instances():
                        if j.name not in seen_names:
                            print(f"\n{j.name}")
                            seen_names.add(j.name)
                            for p in j.get_properties():
                                print(p.name, " ", str(p._get_value_for_individual(j)).split(".")[-1])

                if classe_ == 'MilitaryPerson':
                    for j in ind.instances():
                        if j.name not in seen_names:
                            MP_dictionary[j.name] = {}
                            seen_names.add(j.name)
                            for p in j.get_properties():
                                p_value = str(p._get_value_for_individual(j)).split(".")[-1]
                                if p.name == 'isLocatedIn' or p.name == 'militaryPersonHasMilitaryOrganization' or p.name == 'operates' or p.name == 'carries':
                                    MP_dictionary[j.name][p.name] = p_value

                if classe_ == 'Guarani':
                    for j in ind.instances():
                        guaranis.append(j.name)



            ### COMEÇA A POPULAR O BANCO DE DADOS COM OS DADOS IMPORTADOS ###
            for i in range(len(list(ref_onto.classes()))):
                classe = list(ref_onto.classes())[i]

                if classe.name == 'MilitaryScenario':
                    militaryscenario = str(j.name)

                    ###CRIA CENÁRIO ###
                    #MilitaryScenario.objects.create(name=militaryscenario, description='')
                    #scenario = MilitaryScenario.objects.get(name=militaryscenario) # nomes de cenários precisam ser únicos

                if classe.name == 'MilitaryOrganization':
                    om_name = ''
                    om_type = ''
                    commander = ''
                    for key, value in MO_dictionary.items():
                        print(f"\nKey: {key}")
                        om_name = key
                        for prop, prop_value in value.items():
                            if prop == 'hasMOPowerType':
                                om_type = prop_value
                            if prop == 'isSubordinateTo':
                                commander_name = prop_value
                        if commander_name == '':
                            None
                            #MilitaryOrganization.objects.create(type=om_type,name=om_name,commander=None,scenario=latest_scenario)
                        else:
                            x=1
                            #commander = MilitaryOrganization.objects.get(name=commander_name,scenario=scenario)
                            #MilitaryOrganization.objects.create(type=om_type,name=om_name,commander=commander,scenario=latest_scenario)

                if classe.name == 'Guarani':
                    x=1
                    for g in guaranis:
                        x=1
                        #Guarani.objects.create(name=g,scenario=scenario,VisibilityRange=1000,v_min=95,v_max=3.5,category='Armored')

                if classe.name == 'MilitaryPerson':
                    x=1
                    identifier = ''
                    vehicle = ''
                    by_foot = False
                    for key, value in MP_dictionary.items():
                        print(f"\nKey: {key}")
                        identifier = key
                        for prop, prop_value in value.items():
                            if prop == 'militaryPersonHasMilitaryOrganization':
                                mo_om = prop_value
                                #mo_om = MilitaryOrganization.objects.get(name=mo_om,scenario=scenario)
                            if prop == 'isLocatedIn':
                                vehicle = prop_value
                                carrier = Guarani.objects.get(name=vehicle)
                            if prop == 'carries':
                                by_foot = True
                                #carrier = Carrier.objects.get(Id=1) # by foot


                        #MilitaryPerson.objects.create(Identifier=identifier,Military_Organization=mo_om,CommDevice_Carrier=carrier,scenario=scenario)



        context = {
            "types": types,
            "instances_output": instances_output
        }

        return render(request, 'upload_scenario.html', context)

