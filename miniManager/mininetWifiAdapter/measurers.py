import random
from abc import ABC, abstractmethod
import time
import math

import constants
import threading

class IMeasurer(ABC):
    @abstractmethod
    def run(self):
        pass

class PositionMeasurer(IMeasurer):
    def __init__(self, start, nodes):
        self.__start = start
        self.__nodes = nodes

    def run(self):
        while True:
            time.sleep(constants.MininetConstants.DELAY)
            currentTime = math.floor(time.time() - self.__start)

            positions = {}
            for key in self.__nodes:
                for node in self.__nodes[key]:
                    name = getattr(node.wintfs[0],"name")
                    positions[name] = {"type": key, "position": list(node.position)}

            print({
                constants.MininetConstants.TIME_KEY: currentTime,
                constants.MininetConstants.POSITIONS_KEY: positions
            })

class RadioFrequencyMeasurer(IMeasurer):
    def __init__(self, start, stations, measurements):
        self.__start = start
        self.__stations = stations
        self.__measurements = measurements

    def run(self):
        while True:
            time.sleep(constants.MininetConstants.DELAY)
            currentTime = math.floor(time.time() - self.__start)

            measures, hasAtLeastOne = self.__getValidMeasures(currentTime)
            if not hasAtLeastOne:
                continue

            radioFrequency = []
            for eachNode in self.__stations:
                measObj = {}
                measObj["time"] = currentTime

                for measure in measures:
                    measureName = measure['name']
                    if measure["valid"]:
                        measObj[measureName] = self.__getMetricFromNode(measureName, eachNode)
                    else:
                        measObj[measureName] = ""

                radioFrequency.append(measObj)

            print({
                constants.MininetConstants.TIME_KEY: currentTime,
                constants.MininetConstants.RADIO_FREQUENCY_KEY: radioFrequency
            })
    
    def __isValidMeasurement(self, currentTime, measurement):
        return (currentTime % measurement["period"]) == 0

    def __getValidMeasures(self, currentTime):
        radioFrequencyMeasures = []
        hasAtLeastOne = False
        for measurement in self.__measurements:
            measure = measurement["measure"]
            measure["valid"] = self.__isValidMeasurement(currentTime, measurement)
            radioFrequencyMeasures.append(measure)

            if measure["valid"]:
                hasAtLeastOne = True
        
        radioFrequencyMeasures.append({ "name": "name", "valid": hasAtLeastOne })

        return radioFrequencyMeasures, hasAtLeastOne

    def __getMetricFromNode(self, measureName, node):
        if measureName == "position":
            return list(node.position)

        
        if measureName == "associatedTo":
            if node.wintfs[0].associatedTo:
                return node.wintfs[0].associatedTo.node.wintfs[0].name
            return "None"

        return getattr(node.wintfs[0],measureName)

class PerformanceMeasurer(IMeasurer):
    def __init__(self, start, net, measurements, nodes_om):
        self.__start = start
        self.__net = net
        self.__measurements = measurements
        self.__nodes_om = nodes_om

    def run(self):
        threads = []
        for measurement in self.__measurements:
            t = threading.Thread(target=self.__collectMeasurement, args=(measurement,))
            t.daemon = True
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def __collectMeasurement(self, measurement):
        while True:
            result = self.__getMeasure(measurement["measure"], measurement["source"], measurement["destination"])
            currentTime = math.floor(time.time() - self.__start)
            print({
                constants.MininetConstants.TIME_KEY: currentTime,
                constants.MininetConstants.PERFORMANCE_KEY: result
            })
            time.sleep(measurement["period"])

    def __getMeasure(self, measure, sourceName, destinationName):
        name = measure["name"]

        stations = []  # all stations
        stations_destination = []

        # captura todas as estações
        for node in self.__nodes_om:
            if node["type"] == "station":
                stations.append(node)

        # CHOOSE SOURCE
        s = random.choice(stations)
        source_Name = s["name"]
        source_om_name = s["om_name"]
        source = self.__net.get(source_Name)

        # CHOOSE DESTINATION
        for c in self.__nodes_om:
            if str(c["name"]) != str(s["name"]):
                if c["type"] == "station" and str(c["subkind"]) == str(s["subkind"]):
                    stations_destination.append(c)  # insere todos que possuem o mesmo subkind

        for c in self.__nodes_om:
            if str(c["name"]) != str(s["name"]):
                if c["type"] == "station" and str(c["commander"]) == str(s["military_organization"]):
                    stations_destination.append(c)  # insere os subordinados

        for c in self.__nodes_om:
            if str(c["name"]) != str(s["name"]):
                if c["type"] == "station" and str(c["military_organization"]) == str(s["commander"]):
                        stations_destination.append(c)  # insere o comandante do source

        for c in self.__nodes_om:
            if str(c["name"]) != str(s["name"]):
                if c["type"] == "station" and str(c["subkind"]) != str(s["subkind"]):
                    if c["commander"] == str(s["commander"]):
                        stations_destination.append(c)  # insere aqueles que possuem diferentes kinds mas mesmo commandante

        d = random.choice(stations_destination)
        destination_Name = d["name"]
        destination_om_name = d["om_name"]
        destination = self.__net.get(destination_Name)  # escolhe o destino

        ##METADADOS DOS CONTEÚDOS
        precedence = ['urgente', 'urgentissima', 'preferencial', 'rotina']
        security_level = ['ultra-secreto', 'secreto', 'confidencial', 'reservado', 'ostensivo']
        prec = random.choice(precedence)  # escolhe a precedência aleatóriamente
        sec_level = random.choice(security_level)  # escolhe o security_level aleatóriamente

        if name == "ping":
            value = self.__ping(source, destination)

        #if name == "Iperf":
            #value = self.__iperf(source, destination)

        return {"name": name + "-" + "\nprec: " + prec + "\nsec_level: " + sec_level, # <-- data
                "source": source_Name +"-"+ source_om_name, # + splittedResult2[8],
                "destination": destination_Name + "-" + destination_om_name,
                "value": value}

    def __ping(self, source, destination):
        pingResult = source.cmd('ping', '-c 1 -q', '-I ' + source.wintfs[0].ip, destination.wintfs[0].ip)
        splittedResult = pingResult.split('\r\n')
        return [splittedResult[3], splittedResult[4]]

    def __iperf(self, source, destination):
        iperfResult = source.cmd('iperf -d -c ' + destination.wintfs[0].ip)
        #splittedResult = iperfResult.split('\r\n')
        print(iperfResult)
        return []


