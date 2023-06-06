from django.db import models
from militaryScenarioConf.models import *


class TestPlan(models.Model):
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True)
    author = models.CharField(max_length=50, null=True)
    scenario = models.ForeignKey(MilitaryScenario, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "TestPlan"


class Network(models.Model):
    noise_th = models.IntegerField(default=-91)
    fading_cof = models.IntegerField(default=0)
    adhoc = models.BooleanField(default=False)

    class Meta:
        db_table = "Network"

    def seialize(self):
        return {"adhoc": self.adhoc, "args": {"fading_cof": self.fading_cof, "noise_th": self.noise_th}}


# class NetworkController(models.Model): /vamos usar o Controller do mininet.node
# protocol = models.CharField(max_length=30)

# PModelCatalog works as a catalog of propagation models
class PModelCatalog(models.Model):
    name = models.CharField(max_length=30)
    displayname = models.CharField(max_length=30)

    class Meta:
        db_table = "PModelCatalog"


class MModelCatalog(models.Model):
    name = models.CharField(max_length=30)
    displayname = models.CharField(max_length=30)

    class Meta:
        db_table = "MModelCatalog"


class PropagationModel(models.Model):
    model = models.ForeignKey(PModelCatalog, on_delete=models.CASCADE)

    class Meta:
        db_table = "PropagationModel"


class MobilityModel(models.Model):
    model = models.ForeignKey(MModelCatalog, on_delete=models.CASCADE)

    class Meta:
        db_table = "MobilityModel"


class Measure(models.Model):
    name = models.CharField(max_length=20)
    unit = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = "Measures"


class PerformanceMeasure(models.Model):
    name = models.CharField(max_length=30)
    unit = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = "PerformanceMeasure"


class PropagationParam(models.Model):
    name = models.CharField(max_length=30)
    value = models.FloatField()
    propagationmodel = models.ForeignKey(PropagationModel, on_delete=models.CASCADE)

    class Meta:
        db_table = "PropagationParam"


class MobilityParam(models.Model):
    name = models.CharField(max_length=30)
    value = models.FloatField()
    mobilitymodel = models.ForeignKey(MobilityModel, on_delete=models.CASCADE)

    class Meta:
        db_table = "MobilityParam"

#################################################################
'''
class MilitaryScenario(models.Model):
    Id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=30)

    class Meta:
        db_table = "MilitaryScenario"
        verbose_name = 'MilitaryScenario'
        verbose_name_plural = 'MilitaryScenario'

        def __str__(self):
            return self.Id


class MilitaryOrganizationPowerType(models.Model):
    Id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=30)
    commander = models.ForeignKey("MilitaryOrganizationPowerType", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "MilitaryOrganizationPowerType"
        verbose_name = 'MilitaryOrganizationPowerType'
        verbose_name_plural = 'MilitaryOrganizationPowerTypes'

        def __str__(self):
            return self.Id


# MILITARYORGANIZATION
class MilitaryOrganization(models.Model):
    Id = models.AutoField(primary_key=True, unique=True)
    type = models.ForeignKey("MilitaryOrganizationPowerType", on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=30)
    commander = models.ForeignKey("MilitaryOrganization", on_delete=models.CASCADE, blank=True, null=True)
    scenario = models.ForeignKey("MilitaryScenario", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "MilitaryOrganization"
        verbose_name = 'MilitaryOrganization'
        verbose_name_plural = 'MilitaryOrganization'

        def __str__(self):
            return self.Id

class CommDeviceCarrier(models.Model):
    Id = models.AutoField(primary_key=True, unique=True)
    VisibilityRange = models.FloatField(max_length=30, blank=True, null=True)
    v_min = models.FloatField(max_length=30, blank=True, null=True)
    v_max = models.FloatField(max_length=30, blank=True, null=True)
    scenario = models.ForeignKey("MilitaryScenario", on_delete=models.CASCADE, blank=True, null=True)


class MilitaryPlatform(CommDeviceCarrier):
    ARMORED_CATEGORY = 'armored'
    CATEGORY_CHOICES = (
        (ARMORED_CATEGORY, 'Armored'),
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=ARMORED_CATEGORY)
    kind = models.CharField(max_length=30)
    MilitaryOrganization = models.ForeignKey(MilitaryOrganization, on_delete=models.CASCADE)



class MilitaryPerson(models.Model):
    Identifier = models.CharField(max_length=30)  # 01,02,03...
    MilitaryOrganization = models.ForeignKey(MilitaryOrganization, on_delete=models.CASCADE)
    CommDeviceCarrier = models.ForeignKey(CommDeviceCarrier, on_delete=models.CASCADE, related_name='commdevicecarrier')
    scenario = models.ForeignKey("MilitaryScenario", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "MilitaryPerson"
        verbose_name = 'MilitaryPerson'
        verbose_name_plural = 'MilitaryPerson'

        def __str__(self):
            return self.Identifier

'''
###############################################################

class Node(models.Model):
    name = models.CharField(max_length=30)
    mac = models.CharField(max_length=30)
    militaryperson = models.ForeignKey(MilitaryPerson, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, blank=True, null=True)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)

    class Meta:
        db_table = "Node"

    def getTypeWithAttributes(self):
        nodeTypeToSpecialization = {
            "station": Station,
            "accesspoint": AccessPoint,
            "host": Host,
            "switch": Switch
        }

        return nodeTypeToSpecialization[self.type].objects.get(node_id=self.id).serialize()

    def getInterface(self):
        return Interface.objects.get(node_id=self.id).serialize()

    def serialize(self):
        specializationArgs = self.getTypeWithAttributes()
        interface = self.getInterface()
        subkind = self.militaryperson.Military_Organization.type.name if self.militaryperson.Military_Organization.type else ""
        return {"name": self.name, "mac": self.mac, "type": self.type, "args": specializationArgs,
                "interface": interface, "military_organization": self.militaryperson.Military_Organization.Id,
                "om_name": self.militaryperson.Military_Organization.name, "subkind": subkind,
                "commander": self.militaryperson.Military_Organization.commander,"carrier": self.militaryperson.CommDevice_Carrier}

class Station(models.Model):
    check_position = models.CharField(max_length=1, blank=True, null=True)
    position_node = models.CharField(max_length=30, blank=True, null=True)
    x_min = models.FloatField(max_length=30, blank=True, null=True)
    x_max = models.FloatField(max_length=30, blank=True, null=True)
    y_min = models.FloatField(max_length=30, blank=True, null=True)
    y_max = models.FloatField(max_length=30, blank=True, null=True)
    range = models.FloatField(max_length=30, blank=True, null=True)
    antenna_gain = models.FloatField(max_length=30, blank=True, null=True)
    node = models.OneToOneField(Node, on_delete=models.CASCADE, unique=True)

    class Meta:
        db_table = "Station"

    def serialize(self):
        return {"check_position": self.check_position,
                "position": self.position_node, "x_min": self.x_min, "x_max": self.x_max, "y_min": self.y_min,
                "y_max": self.y_max, "range": self.range, "antenna_gain": self.antenna_gain}


class Host(models.Model):
    node = models.OneToOneField(Node, on_delete=models.CASCADE, unique=True)

    class Meta:
        db_table = "Host"

    def serialize(self):
        return {}


class Switch(models.Model):
    node = models.OneToOneField(Node, on_delete=models.CASCADE, unique=True)

    class Meta:
        db_table = "Switch"

    def serialize(self):
        return {}


class AccessPoint(models.Model):
    ssid = models.CharField(max_length=30)  # ssid=['ssid1', 'mesh']
    mode = models.CharField(max_length=30)
    channel = models.CharField(max_length=30)
    wlans = models.IntegerField(max_length=30)
    check_position = models.CharField(max_length=1, blank=True, null=True)
    position_node = models.CharField(max_length=30, blank=True, null=True)
    x_min = models.FloatField(max_length=30, blank=True, null=True)
    x_max = models.FloatField(max_length=30, blank=True, null=True)
    y_min = models.FloatField(max_length=30, blank=True, null=True)
    y_max = models.FloatField(max_length=30, blank=True, null=True)
    range = models.FloatField(max_length=30, blank=True, null=True)
    antenna_gain = models.FloatField(max_length=30, blank=True, null=True)
    node = models.OneToOneField(Node, on_delete=models.CASCADE, unique=True)

    class Meta:
        db_table = "AccessPoint"

    def serialize(self):
        return {"ssid": [self.ssid, "mesh"], "mode": self.mode, "channel": self.channel, "wlans": self.wlans,
                "check_position": self.check_position,
                "position": self.position_node, "x_min": self.x_min, "x_max": self.x_max, "y_min": self.y_min,
                "y_max": self.y_max, "range": self.range, "antenna_gain": self.antenna_gain}


class InterfacePowerType(models.Model):
    name = models.CharField(max_length=30)
    txpower = models.IntegerField(default=15)
    frequency = models.IntegerField(default=15)

    class Meta:
        db_table = "InterfacePowerType"

    def serialize(self):
        return {}

class Interface(models.Model):
    name = models.CharField(max_length=30)
    ip_intf0 = models.CharField(max_length=30)
    ip_intf1 = models.CharField(max_length=30)
    txpower_intf0 = models.IntegerField(default=15)
    txpower_intf1 = models.IntegerField(default=15)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)

    class Meta:
        db_table = "Interface"

    def serialize(self):
        args = {"ip_intf0": self.ip_intf0, "ip_intf1": self.ip_intf1,
                "txpower_intf0": self.txpower_intf0, "txpower_intf1": self.txpower_intf1}
        return {"id": self.id, "name": self.name, "args": args}


class Link(models.Model):
    int1 = models.ForeignKey(Interface, related_name='int1', on_delete=models.CASCADE, null=True)
    int2 = models.ForeignKey(Interface, related_name='int2', on_delete=models.CASCADE, null=True)
    bw = models.IntegerField(blank=True, null=True)
    delay = models.IntegerField(blank=True, null=True)
    loss = models.IntegerField(blank=True, null=True)
    max_queue_size = models.IntegerField(blank=True, null=True)
    jitter = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "Link"

    def serialize(self):
        args = {"bw": self.bw, "delay": self.delay, "loss": self.loss, "max_queue_size": self.max_queue_size,
                "jitter": self.jitter}
        return {"node1": self.int1.node.name, "node2": self.int2.node.name, "args": args}


class Mobility(models.Model):
    tempo = models.FloatField()
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    node = models.ForeignKey(Node, on_delete=models.CASCADE)

    class Meta:
        db_table = "Mobility"


class Position(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    node = models.ForeignKey(Node, on_delete=models.CASCADE)

    class Meta:
        db_table = "Position"


class Configuration(models.Model):
    medicao_schema = models.TextField()
    propagationmodel = models.ForeignKey(PropagationModel, on_delete=models.CASCADE, null=True)
    mobilitymodel = models.ForeignKey(MobilityModel, on_delete=models.CASCADE, null=True)
    stop_time = models.IntegerField(blank=True,null=True)
    network = models.ForeignKey(Network, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "Configuration"

    def getNodes(self):
        result = []
        nodes = Node.objects.filter(network_id=self.network.id)

        for node in nodes:
            nodeObj = node.serialize()
            result.append(nodeObj)

        return result

    def getLinks(self, nodes):
        links = []
        for node in nodes:
            foundedLinks = Link.objects.filter(int1_id=node["interface"]["id"]).all()
            for link in foundedLinks:
                links.append(link.serialize())

        return links

    def getMeasurements(self):
        result = []
        measurements = Measurement.objects.filter(config_id=self.id)
        for measurement in measurements:
            result.append({"period": measurement.period, "measure": {"name": measurement.measure.name}})

        return result

    def getPerformanceMeasurements(self):
        result = []
        measurements = PerformanceMeasurement.objects.filter(config_id=self.id)
        for measurement in measurements:
            result.append(
                {"period": measurement.period, "source": measurement.source, "destination": measurement.destination,
                 "measure": {"name": measurement.measure.name}, "random_choice": measurement.random_choice})

        return result

    def getPropagationModel(self):
        propagationmodel = self.propagationmodel
        args = {}
        params = PropagationParam.objects.filter(propagationmodel_id=propagationmodel.id)
        for param in params:
            args[param.name] = param.value

        return {"model": propagationmodel.model.name, "args": args}

    def getMobilityModel(self):
        mobilitymodel = self.mobilitymodel
        args = {}
        params = MobilityParam.objects.filter(mobilitymodel_id=mobilitymodel.id)
        for param in params:
            args[param.name] = param.value

        return {"model": mobilitymodel.model.name, "args": args}

    def getConfigurationObj(self):
        nodes = self.getNodes()
        return {
            "network": self.network.seialize(),
            "radioFrequencyMeasurements": self.getMeasurements(),
            "performanceMeasurements": self.getPerformanceMeasurements(),
            "propagationModel": self.getPropagationModel(),
            "mobilityModel": self.getMobilityModel(),
            "nodes": nodes,
            "links": self.getLinks(nodes)
        }


class PerformanceMeasurement(models.Model):
    period = models.IntegerField()
    measure = models.ForeignKey(PerformanceMeasure, on_delete=models.CASCADE)  # ping
    config = models.ForeignKey(Configuration, on_delete=models.CASCADE)
    source = models.CharField(max_length=20)
    destination = models.CharField(max_length=20)
    random_choice = models.IntegerField(default=1)

    class Meta:
        db_table = "PerformanceMeasurement"


class Measurement(models.Model):
    period = models.IntegerField()
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE)
    config = models.ForeignKey(Configuration, on_delete=models.CASCADE)

    class Meta:
        db_table = "Measurement"


class Version(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    test_plan = models.ForeignKey(TestPlan, models.CASCADE, blank=True, null=True, unique=False)
    configuration = models.OneToOneField(Configuration, models.CASCADE, unique=True, blank=True, null=True)

    class Meta:
        db_table = "Version"