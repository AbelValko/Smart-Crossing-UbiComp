import numpy as np
from math import floor
import SimulationParameters as params
import turtle
import gc

class IntersectionSimulator:

    def __init__(self):
        self.intersection = Intersection()
        self.intersection.generateArrivalDetectionTimes()
        self.queue = []
        self.vehicleTurtles = []
        self.totalCars = 0
        self.totalTime = 0
    def updateVehiclePositions(self, time):
        for i, vehicle in enumerate(self.queue):
            vehicle.updatePosition(time)
            if params.ANIMATION_ON:
                for j, vehicleTurtle in enumerate(self.vehicleTurtles):
                    if vehicleTurtle.leaving is False and vehicleTurtle.updated is False:
                        if vehicleTurtle.source == vehicle.source and vehicleTurtle.destination == vehicle. destination:
                            vehicleTurtle.distance = vehicle.distance
                            vehicleTurtle.updated = True
                            if floor(vehicle.distance) <= 1 and vehicleTurtle.leaving is not True:
                                vehicleTurtle.vehicleTurn()
                            else:
                                vehicleTurtle.updatePosition(time)
                            break
            if vehicle.distance <= 1:  # TODO
                self.totalCars += 1
                self.totalTime += vehicle.assignedArrivalTime - vehicle.detectionTime
                del self.queue[i]
        if params.ANIMATION_ON:
            for i, vehicleTurtle in enumerate(self.vehicleTurtles):
                if vehicleTurtle.updated is False:
                    vehicleTurtle.updatePosition(time)
                vehicleTurtle.updated = False
                if vehicleTurtle.distance <= -100:
                    self.vehicleTurtles[i].clear()
                    self.vehicleTurtles[i].ht()
                    del self.vehicleTurtles[i]
        gc.collect()

    def probeForNewVehicles(self, time):
        newVehicles = []
        for i, road in enumerate(self.intersection.roads):
            if road.arrivalDetectionTimes:
                nextVehicleTime = road.arrivalDetectionTimes[0]
                while time >= nextVehicleTime:
                    newVehicle = Vehicle(i, nextVehicleTime, time - nextVehicleTime)
                    newVehicles.append(newVehicle)
                    if params.ANIMATION_ON:
                        self.vehicleTurtles.insert(0, VehicleTurtle(newVehicle))
                    del road.arrivalDetectionTimes[0]
                    if road.arrivalDetectionTimes:
                        nextVehicleTime = road.arrivalDetectionTimes[0]
                    else:
                        break
        return newVehicles

    def addNewVehicles(self, newVehicles):
        self.queue += newVehicles
        return


class Intersection:

    def __init__(self):
        self.numberOfRoads = params.NUMBER_OF_ROADS
        self.roads = []
        for i in range(self.numberOfRoads):
            self.roads.append(Road(i, params.MEAN_INTER_ARRIVAL_TIMES[i], params.ROAD_LENGTHS[i]))

    def generateArrivalDetectionTimes(self):
        for road in self.roads:
            road.generateRoadArrivalTimes()

class Road:

    def __init__(self, ID, meanInterArrivalTime, length):
        self.ID = ID
        self.meanInterArrivalTime = meanInterArrivalTime
        self.length = length

    def generateRoadArrivalTimes(self):
        length = floor(params.TIME_MAX / self.meanInterArrivalTime * 1.2)
        arrivals = np.random.exponential(scale=self.meanInterArrivalTime, size=(length))
        for i in range(1, len(arrivals)):
            arrivals[i] += arrivals[i - 1] + params.INTER_CAR_SPACE / params.ARRIVAL_SPEED
        self.arrivalDetectionTimes = arrivals.tolist()


class VehicleTurtle(turtle.Turtle):  # TODO DELEGATION

    def __init__(self, vehicle):
        self.source = vehicle.source
        self.detectionTime = vehicle.detectionTime
        self.destination = vehicle.destination
        self.distance = vehicle.distance
        self.leaving = False
        self.previousDistance = self.distance
        self.createTurtle()
        self.updated = False

    def createTurtle(self):
        turtle.Turtle.__init__(self, visible=False)
        self.penup()
        self.shape("triangle")
        self.color("red")
        self.turtlesize(0.5, 0.5)
        if self.source == 0:
            self.setpos(-params.ROAD_LENGTHS[self.source], -10)
            self.seth(0)
        elif self.source == 1:
            self.setpos(10, -params.ROAD_LENGTHS[self.source])
            self.seth(90)
        elif self.source == 2:
            self.setpos(params.ROAD_LENGTHS[self.source], 10)
            self.seth(180)
        elif self.source == 3:
            self.setpos(-10, params.ROAD_LENGTHS[self.source])
            self.seth(270)
        self.showturtle()

    def __repr__(self):
        return "<V %s-%s d:%s l:%s u:%s>" % (self.source, self.destination, floor(self.distance), self.leaving, self.updated)

    def updatePosition(self, timeNow, vehicleInFront=None):
        if self.leaving is False:
            self.forward(self.previousDistance - self.distance)
            self.previousDistance = self.distance
        else:
            self.forward(30)
            self.distance -= 30
        pass

    def vehicleTurn(self):
        self.leaving = True
        if self.destination == 0:
            self.goto(0, 10)
            self.seth(180)
        elif self.destination == 1:
            self.goto(-10, 0)
            self.seth(270)
        elif self.destination == 2:
            self.goto(0, -10)
            self.seth(0)
        elif self.destination == 3:
            self.goto(10, 0)
            self.seth(90)
        self.color("green")
        self.forward(15)

class Vehicle():  # TODO DELEGATION

    def __init__(self, source, detectionTime, initialTravelTime):
        self.source = source
        self.detectionTime = detectionTime
        self.destination = np.random.choice(params.CROSSING_CONNECTIONS[self.source], p=params.TURN_PROBABILITIES[self.source])
        self.distance = params.ROAD_LENGTHS[self.source] - initialTravelTime * params.ARRIVAL_SPEED
        self.assignedArrivalTime = None

    def __repr__(self):
        return "<V %s-%s d:%s>" % (self.source, self.destination, floor(self.distance))

    def updatePosition(self, timeNow, vehicleInFront=None):
        if self.assignedArrivalTime is not None:
            self.distance -= params.RESOLUTION * self.distance / (self.assignedArrivalTime - timeNow)
        else:
            self.distance -= params.ARRIVAL_SPEED * params.RESOLUTION
        pass
