
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
from configurator.models import *

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
                        new_guarani_name = 'guarani'+scenario_name
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
        scenario = ''
        MO_dictionary = {}
        commander_name = ''
        MP_dictionary = {}
        guaranis_dictionary = {}
        CommDevices_dictionary = {}
        Interfaces_dictionary = {}
        guarani_om = ''

        testplan=''
        network=''

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
                        if j.name not in seen_names:
                            guaranis_dictionary[j.name] = {}
                            seen_names.add(j.name)
                            for p in j.get_properties():
                                p_value = str(p._get_value_for_individual(j)).split(".")[-1]
                                if p.name == 'belongsTo':
                                    guaranis_dictionary[j.name][p.name] = p_value


                if classe_ == 'CommDevice':
                    for j in ind.instances():
                        #print(j.hasInterface[0])
                        #print(j.hasInterface[1])
                        print(j.MAC)
                        if j.name not in seen_names:
                            CommDevices_dictionary[j.name] = {}
                            seen_names.add(j.name)
                            p_value0 = str(j.hasInterface[0]).split(".")[-1]
                            p_value1 = str(j.hasInterface[1]).split(".")[-1]
                            mac = str(j.MAC).strip("[]")
                            mac = mac.strip("'")
                            CommDevices_dictionary[j.name]['hasInterface'] = [p_value0, p_value1]
                            CommDevices_dictionary[j.name]['MAC'] = mac

                if classe_ == 'UeUp' or classe_ == 'UeDown':
                    for j in ind.instances():
                        #print(j.IP)
                        #print(j.Txpower)
                        if j.name not in seen_names:
                            Interfaces_dictionary[j.name] = {}
                            seen_names.add(j.name)

                            ip = str(j.IP).strip("[]")
                            ip = ip.strip("'")

                            txpower = str(j.Txpower).strip("[]")
                            txpower = txpower.strip("'")
                            txpower = float(txpower)

                            Coverage = str(j.Coverage).strip("[]")
                            Coverage = Coverage.strip("'")
                            Coverage = float(Coverage)

                            AntennaGain = str(j.AntennaGain).strip("[]")
                            AntennaGain = AntennaGain.strip("'")
                            AntennaGain = float(AntennaGain)

                            Interfaces_dictionary[j.name]['IP'] = ip
                            Interfaces_dictionary[j.name]['txpower'] = txpower
                            Interfaces_dictionary[j.name]['Coverage'] = Coverage
                            Interfaces_dictionary[j.name]['AntennaGain'] = AntennaGain

            ### COMEÇA A POPULAR O BANCO DE DADOS COM OS DADOS IMPORTADOS ###
            #for i in range(len(list(ref_onto.classes()))):
            #    classe = list(ref_onto.classes())[i]

            if 'MilitaryScenario' in [classe.name for classe in ref_onto.classes()]:
                #militaryscenario = str(j.name)

                ###CRIA CENÁRIO ###

                scenario_id = MilitaryScenario.objects.latest('Id').Id + 1
                MilitaryScenario.objects.create(Id=scenario_id, name=scenario_name, description='')
                scenario = MilitaryScenario.objects.get(name=scenario_name) # nomes de cenários precisam ser únicos

            if 'MilitaryOrganization' in [classe.name for classe in ref_onto.classes()]:
                om_name = ''
                om_type = ''
                commander = ''
                for key, value in MO_dictionary.items():
                    print(f"\nKey: {key}")
                    om_name = key
                    commander_name == ''
                    for prop, prop_value in value.items():
                        if prop == 'hasMOPowerType':
                            om_type = prop_value
                            om_type = MilitaryOrganizationPowerType.objects.get(name=om_type)
                        if prop == 'isSubordinateTo':
                            commander_name = prop_value
                    if commander_name == '':
                        om_id = MilitaryOrganization.objects.latest('Id').Id + 1
                        MilitaryOrganization.objects.create(Id=om_id,type=om_type,name=om_name,commander=None,scenario=scenario)
                    else:
                        commander = MilitaryOrganization.objects.get(name=commander_name,scenario=scenario)
                        om_id = MilitaryOrganization.objects.latest('Id').Id + 1
                        MilitaryOrganization.objects.create(Id=om_id,type=om_type,name=om_name,commander=commander,scenario=scenario)

            if 'Guarani' in [classe.name for classe in ref_onto.classes()]:
                for key, value in guaranis_dictionary.items():
                    #print(f"\nKey: {key}")
                    guarani_name = key
                    guarani_om == ''
                    for prop, prop_value in value.items():
                        if prop == 'belongsTo':
                            guarani_om = prop_value
                            guarani_om = MilitaryOrganization.objects.get(name=guarani_om,scenario=scenario)
                    try:
                        g_id = Guarani.objects.latest('Id').Id + 1
                    except:
                        g_id = 0
                    Guarani.objects.create(Id=g_id,name=guarani_name,scenario=scenario,VisibilityRange=1000,v_min=95,v_max=3.5,category='Armored', Military_Organization=guarani_om)

            if 'MilitaryPerson' in [classe.name for classe in ref_onto.classes()]:
                identifier = ''
                vehicle = ''
                by_foot = False
                for key, value in MP_dictionary.items():
                    #print(f"\nKey: {key}")
                    identifier = key
                    for prop, prop_value in value.items():
                        if prop == 'militaryPersonHasMilitaryOrganization':
                            mo_om = prop_value
                            mo_om = MilitaryOrganization.objects.get(name=mo_om,scenario=scenario)
                        if prop == 'isLocatedIn':
                            vehicle = prop_value
                            carrier = Guarani.objects.get(name=vehicle, scenario=scenario)
                        if prop == 'carries':
                            by_foot = True
                            carrier = Carrier.objects.get(Id=1) # by foot

                    MilitaryPerson.objects.create(Identifier=identifier,Military_Organization=mo_om,CommDevice_Carrier=carrier,scenario=scenario)

            ### COMEÇA A CRIAR OS ELEMENTOS ESPECÍFICOS DO MINIMANAGER E DA REDE ###

            ###CRA PLANO DE TESTE###
            testplan = TestPlan.objects.create(name=filename,description="imported owl",author="",scenario=scenario)

            ###CRIA NETWORK###

            network = Network.objects.create(noise_th=-91,fading_cof=0,adhoc=True)

            ###CRIA CONFIGURATION###
            # Escape the XML string properly
            xml_string = '<?xml version="1.0" encoding="UTF-8" ?><xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"><xs:element name="result"><xs:complexType><xs:all><xs:element name="radioFrequency"><xs:complexType><xs:sequence><xs:element name="instant" maxOccurs="unbounded"><xs:complexType><xs:sequence><xs:element name="station" minOccurs="0" maxOccurs="unbounded"><xs:complexType><xs:all><xs:element name="rssi" type="xs:string"/><xs:element name="channel" type="xs:string"/><xs:element name="band" type="xs:string"/><xs:element name="txpower" type="xs:string"/><xs:element name="ip" type="xs:string"/><xs:element name="position" type="xs:string"/><xs:element name="associatedTo" type="xs:string"/></xs:all><xs:attribute name="name" type="xs:string" use="required"/></xs:complexType></xs:element></xs:sequence><xs:attribute name="time" type="xs:string" use="required"/></xs:complexType></xs:element></xs:sequence></xs:complexType></xs:element><xs:element name="performance"><xs:complexType><xs:sequence><xs:element name="instance" minOccurs="0" maxOccurs="unbounded"><xs:complexType><xs:all><xs:element name="value" type="xs:string"/></xs:all><xs:attribute name="name" type="xs:string" use="required"/><xs:attribute name="time" type="xs:string" use="required"/><xs:attribute name="source" type="xs:string" use="required"/><xs:attribute name="destination" type="xs:string" use="required"/></xs:complexType></xs:element></xs:sequence></xs:complexType></xs:element></xs:all><xs:attribute name="roundID" type="xs:string" use="required"/></xs:complexType></xs:element></xs:schema>'

            propagationmodel=PropagationModel.objects.first()
            mobilitymodel=MobilityModel.objects.first()
            configuration = Configuration.objects.create(medicao_schema=xml_string,propagationmodel=propagationmodel,mobilitymodel=mobilitymodel,network=network)

            ###CRIA MEASUREMENTS COM VALOR 0 PARA O USUÁRIO EDITAR DEPOIS###
            rssi = Measure.objects.get(name='rssi')
            channel = Measure.objects.get(name='channel')
            band = Measure.objects.get(name='band')
            txpower = Measure.objects.get(name='txpower')
            ip = Measure.objects.get(name='ip')
            position = Measure.objects.get(name='position')
            associatedTo = Measure.objects.get(name='associatedTo')
            Measurement.objects.create(period=1,measure=rssi,config=configuration)
            Measurement.objects.create(period=1, measure=channel, config=configuration)
            Measurement.objects.create(period=1, measure=band, config=configuration)
            Measurement.objects.create(period=1, measure=txpower, config=configuration)
            Measurement.objects.create(period=1, measure=ip, config=configuration)
            Measurement.objects.create(period=1, measure=position, config=configuration)
            Measurement.objects.create(period=1, measure=associatedTo, config=configuration)

            ####CRIA VERSION###
            Version.objects.create(name=filename+"_version",test_plan=testplan,configuration=configuration)

            ###CRIA NODES###
            stop = False
            node = ''
            node_name = ''
            for key, value in MP_dictionary.items():
                identifier = key
                for prop, prop_value in value.items():
                    if prop == 'operates':
                        interface = prop_value
                        #Encontra o commdevide correspondente
                        for key, value in CommDevices_dictionary.items():
                            node = key
                            for prop, prop_value in value.items():
                                if prop == 'hasInterface':
                                    interface_ = prop_value
                                    if interface in interface_:
                                        node_name = node
                                        mac_address = CommDevices_dictionary[node_name]['MAC']
                                        stop = True
                                        break
                                if stop == True:
                                    break

                        mp = MilitaryPerson.objects.get(Identifier=identifier,scenario=scenario)
                        Node.objects.create(name=node_name, mac=mac_address,militaryperson=mp,type="station",network=network)
                        node_ = Node.objects.get(name=node_name,network=network)
                        Station.objects.create(node=node_,check_position=2,x_min=0,x_max=0,y_min=0,y_max=0)

                        ###CRIA PerformanceMeasurement ###
                        measure = PerformanceMeasure.objects.get(name='ping')
                        PerformanceMeasurement.objects.create(period=1,measure=measure,config=configuration,source='None',destination='None',random_choice=1)

                        ###CRIA INTERFACES###
                        node_interface0 = CommDevices_dictionary[node_name]['hasInterface'][0]
                        node_interface1 = CommDevices_dictionary[node_name]['hasInterface'][1]

                        ip_interf0 = Interfaces_dictionary[node_interface0]['IP']
                        ip_interf1 = Interfaces_dictionary[node_interface1]['IP']

                        txpower_intf0 = Interfaces_dictionary[node_interface0]['txpower']
                        txpower_intf1 = Interfaces_dictionary[node_interface1]['txpower']

                        range_intf0 = Interfaces_dictionary[node_interface0]['Coverage']
                        range_intf1 = Interfaces_dictionary[node_interface1]['Coverage']

                        antenna_gain_intf0 = Interfaces_dictionary[node_interface0]['AntennaGain']
                        antenna_gain_intf1 = Interfaces_dictionary[node_interface1]['AntennaGain']

                        Interface.objects.create(name=interface, ip_intf0=ip_interf0, ip_intf1=ip_interf1, txpower_intf0=txpower_intf0, txpower_intf1=txpower_intf1,
                                                 range_intf0=range_intf0, range_intf1=range_intf1, antenna_gain_intf0=antenna_gain_intf0,
                                                 antenna_gain_intf1=antenna_gain_intf1, node=node_)

        context = {
            "types": types,
            "instances_output": instances_output
        }

        return render(request, 'upload_scenario.html', context)

