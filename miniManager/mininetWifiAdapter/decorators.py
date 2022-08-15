from abc import ABC, abstractmethod
import time

from mininet.node import Controller
from mn_wifi.link import adhoc

from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, mesh
from mn_wifi.wmediumdConnector import interference
from json import dumps
from requests import put
from mininet.util import quietRun
from os import listdir, environ
import re

class MininetDecoratorComponent(ABC):
    @abstractmethod
    def configure(self):
        pass

    @abstractmethod
    def getNetwork(self):
        pass
class MininetNetwork(MininetDecoratorComponent):
    def __init__(self, networkAttributes, nodes, isAdhoc):
        self.__network = None
        self.__nodes = nodes
        self.__networkAttributes = networkAttributes
        self.__isAdhoc = isAdhoc

    def getNetwork(self):
        return self.__network

    def configure(self):
        info("*** Creating network\n")

        if self.__isAdhoc:
            self.__network = Mininet_wifi(**self.__networkAttributes)
        else:
            self.__network = Mininet_wifi(controller=Controller, **self.__networkAttributes)
            self.__network.addController('c1')
        
        info("*** Creating nodes\n")
        for node in self.__nodes:
            if node["type"] == "station":
                self.__network.addStation(node["name"], **node["args"], **node["interface"]["args"])
            if node["type"] == "accesspoint":
                self.__network.addAccessPoint(node["name"], **node["args"], **node["interface"]["args"])
            if node["type"] == "host":
                self.__network.addHost(node["name"], **node["args"], **node["interface"]["args"])
            if node["type"] == "switch":
                self.__network.addSwitch(node["name"], **node["args"], **node["interface"]["args"])

        info("*** Configuring wifi nodes\n")
        self.__network.configureWifiNodes() #self.__network --> net

class MininetBaseDecorator(MininetDecoratorComponent):
    def __init__(self, component):
        self.__network = None
        self.__component = component

    def getNetwork(self):
        return self.__network

    def configure(self):
        self.__component.configure()
        self.__network = self.__component.getNetwork()

class PropagationModelDecorator(MininetBaseDecorator):
    ARGS_MAP = {
        "exponent": "exp"
    }

    def __init__(self, component, propagationModel):
        super().__init__(component)
        self.__propagationModel = propagationModel
        self.__args = {}
        self.__parseArgs()

    def __parseArgs(self):
        self.__args = {}
        for arg in self.__propagationModel["args"]:
            self.__args[self.ARGS_MAP[arg]] = self.__propagationModel["args"][arg]

    def configure(self):
        info("***Setting Propagation Model\n")
        super().configure()
        self.getNetwork().setPropagationModel(model=self.__propagationModel["model"], **self.__args)

class MobilityModelDecorator(MininetBaseDecorator):
    ARGS_MAP = {
        "seed": "seed",
        "min_velocidade": "min_v",
        "max_velocidade": "max_v",
        "min_x": "min_x",
        "max_x": "max_x",
        "min_y": "min_y",
        "max_y": "max_y",
        "min_z": "min_z",
        "max_z": "max_z",
    }

    def __init__(self, component, mobilityModel):
        super().__init__(component)
        self.__mobilityModel = mobilityModel
        
        self.__args = {}
        self.__parseArgs()

    def __parseArgs(self):
        self.__args = {}
        for arg in self.__mobilityModel["args"]:
            value = self.__mobilityModel["args"][arg]
            if arg == "seed":
                value = int(value)

            self.__args[self.ARGS_MAP[arg]] = value

    def configure(self):
        info("***Setting Mobility Model\n")
        super().configure()
        self.getNetwork().setMobilityModel(time=0, model=self.__mobilityModel["model"], **self.__args)

class NetworkStarterDecorator(MininetBaseDecorator):
    def __init__(self, component, links, isAdhoc):
        super().__init__(component)
        self.__links = links
        self.__isAdhoc = isAdhoc
    
    def configure(self):
        super().configure()
        info("*** Starting network\n")
        network = self.getNetwork()

        for link in self.__links:
            network.addLink(link["node1"], link["node2"], **link["args"])

        info("*** Creating mesh links\n")
        for ap in network.aps:
            network.addLink(ap, intf=str(ap.name)+'-wlan2', cls=mesh, ssid='mesh-ssid', channel=5)

        network.telemetry(nodes=network.stations, single=True)
        network.build()

        if self.__isAdhoc:
            for station in network.stations:
                network.addLink(station, cls=adhoc, intf=station.wintfs[0].name, ssid='adhocNet')
        else:
            network.get("c1").start()
            for ap in network.aps:
                network.get(ap.name).start([network.get("c1")])

            for s in network.switches:
                network.get(s.name).start([network.get("c1")])

            ### CÓDIGO PARA RODAR NO MININET DASHBOARD

            for ap in network.aps:
                ap.cmd('iw dev %s-mp2 interface add %s-mon0 type monitor' % (ap.name, ap.name))  # iw dev to view the available WiFi hardware/interfaces
                # ap2.cmd('iw dev %s-mp2 interface add %s-mon0 type monitor' % (ap2.name, ap2.name)) # add mon to use monitor mode
                ap.cmd('ifconfig %s-mon0 up' % ap.name)  # ativar interface
                # ap2.cmd('ifconfig %s-mon0 up' % ap2.name) # ativar interface

            ifname = 'enp2s0'  # have to be changed to your own iface!
            collector = environ.get('COLLECTOR', '127.0.0.1')
            sampling = environ.get('SAMPLING', '10')
            polling = environ.get('POLLING', '10')
            sflow = 'ovs-vsctl -- --id=@sflow create sflow agent=%s target=%s ' \
                    'sampling=%s polling=%s --' % (ifname, collector, sampling, polling)

            for ap in network.aps:
                sflow += ' -- set bridge %s sflow=@sflow' % ap
                info(' '.join([ap.name for ap in network.aps]))
                quietRun(sflow)

            agent = '127.0.0.1'
            topo = {'nodes': {}, 'links': {}}
            for ap in network.aps:
                topo['nodes'][ap.name] = {'agent': agent, 'ports': {}}

            path = '/sys/devices/virtual/mac80211_hwsim/'
            for child in listdir(path):
                dir_ = '/sys/devices/virtual/mac80211_hwsim/' + '%s' % child + '/net/'
                for child_ in listdir(dir_):
                    node = child_[:3]
                    if node in topo['nodes']:
                        ifindex = open(dir_ + child_ + '/ifindex').read().split('\n', 1)[0]
                        topo['nodes'][node]['ports'][child_] = {'ifindex': ifindex}

            path = '/sys/devices/virtual/net/'
            for child in listdir(path):
                parts = re.match('(^.+)-(.+)', child)
                if parts is None: continue
                if parts.group(1) in topo['nodes']:
                    ifindex = open(path + child + '/ifindex').read().split('\n', 1)[0]
                    topo['nodes'][parts.group(1)]['ports'][child] = {'ifindex': ifindex}
            #
            # linkName = '%s-%s' % (ap1.name, ap2.name)
            # topo['links'][linkName] = {'node1': ap1.name, 'port1': 'ap1-mp2', 'node2': ap2.name, 'port2': 'ap2-mp2'}
            # linkName = '%s-%s' % (ap1.name, ap2.name)
            # topo['links'][linkName] = {'node1': ap1.name, 'port1': ap1.wintfs[0].name, 'node2': ap2.name, 'port2': ap2.wintfs[0].name} #interface name

            put('http://127.0.0.1:8008/topology/json', data=dumps(topo))
