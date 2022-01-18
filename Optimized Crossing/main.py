import simulation as sim
import SimulationParameters as params
import time
import copy
from math import floor
import gc

if params.ANIMATION_ON:
    import turtle
    wn = turtle.Screen()
    wn.title("Demo")
    wn.bgcolor("gray")
    wn.setup(800, 800)
    wn.bgpic("bg.gif")
    wn.update()
    wn.delay(0)

def main():
    if params.ANIMATION_ON:
        time.sleep(3)
    timeNow = 0
    simulator = sim.IntersectionSimulator()
    controller = IntersectionController()
    lastQueueLen = 0
    while timeNow <= (sim.params.TIME_MAX + 50):
        if params.ANIMATION_ON:
            time.sleep(0.1)
        simulator.updateVehiclePositions(timeNow)
        newVehicles = simulator.probeForNewVehicles(timeNow)
        controller.updateSlots()
        for vehicle in newVehicles:
            print("____ASSIGNING VEHICLE____")
            print("New vehicle: %s" % vehicle)
            controller.maxDepth = 0
            slots, costs = controller.allocateSlots(vehicle)
            if slots is None:
                print("ERROR - CONGESTION")  # TODO
                exit()
            else:
                controller.slots = slots
                print("Cost: %s" % costs)
                print("Iterations: %s" % controller.maxDepth)
            print("Current slots: %s" % controller.slots)
        controller.assignArrivalTimesToSlots(timeNow)
        flattenedSlots = [item for sublist in controller.slots for item in sublist]
        simulator.queue = flattenedSlots
        #simulator.addNewVehicles(newVehicles)
        timeNow += params.RESOLUTION
        if len(simulator.queue) != lastQueueLen:
            print("Number of cars in queue %s" % len(simulator.queue))
        lastQueueLen = len(simulator.queue)
        gc.collect()
    print("SIMULATION COMPLETE")
    print("Total number of cars passed: %s" % simulator.totalCars)
    print("Total travel time: %s" % simulator.totalTime)

class IntersectionController:

    def __init__(self):
        self.slots = [[] for i in range(params.NUMBER_OF_SLOTS)]
        self.maxDepth = 0

    def updateSlots(self):
        for slotIndex, slot in enumerate(self.slots):
            if len(slot) > 2:
                print("BIG ERROR - slot length exceeds 2")
                exit()
            for i, vehicle in enumerate(slot):
                if vehicle.distance <= 1:
                    del slot[i]
            if slot != []:
                firstFeasibleSlot = floor((slot[0].distance / params.SPEED_LIMIT) / params.SLOT_SIZE)
                for i in range(firstFeasibleSlot, slotIndex):
                    if self.slots[i] == []:
                        self.slots[i] = slot
                        self.slots[slotIndex] = []

    def allocateSlots(self, newVehicle, slots=None, lockedSlots=[]):
        self.maxDepth += 1
        slotAllocated = False
        cost = 99999
        if slots is None:
            slots = copy.deepcopy(self.slots)
        slotsToReturn = copy.deepcopy(slots)
        #print("Assigning: %s" % newVehicle)
        #print("To Slots: %s" % slots)
        #print("With locked: %s" % lockedSlots)
        firstFeasibleSlot = floor((newVehicle.distance / params.SPEED_LIMIT) / params.SLOT_SIZE)
        #print("firstFeasibleSlot: %s" % firstFeasibleSlot)
        if isSlotAvailable(slots, firstFeasibleSlot, newVehicle, lockedSlots):
            #print("Is free")
            slotAllocated = True
            slotsToReturn[firstFeasibleSlot].append(newVehicle)
            cost = 0
        else:
            suggestedSlot = copy.copy(firstFeasibleSlot)
            while isSlotAvailable(slots, suggestedSlot, newVehicle, lockedSlots) is not True:
                #print("Checking: %s in slot: %s" % (newVehicle, suggestedSlot))
                conflictInFront = existsConflictInFront(slots, suggestedSlot, newVehicle, lockedSlots)
                if conflictInFront:
                    #print("Conflict in front found")
                    break
                elif existsConflictBehind(slots, suggestedSlot, newVehicle, lockedSlots) is False and isSlotLocked(lockedSlots, suggestedSlot) is False:
                    #print("Feasible")
                    if len(slots[suggestedSlot]) == 2:
                        #print("Skipping double slots")
                        suggestedSlot += 1
                        if suggestedSlot >= params.NUMBER_OF_SLOTS:
                            break
                        continue
                    newSlotArrangement = copy.deepcopy(slots)  # TODO
                    newSlotArrangement[suggestedSlot] = [newVehicle]
                    newLockedSlots = copy.copy(lockedSlots)
                    newLockedSlots.append(suggestedSlot)
                    vehiclesToAllocate = copy.copy(slots[suggestedSlot])
                    suggestedSlotArrangement, suggestedCost = self.allocateSlots(vehiclesToAllocate[0], newSlotArrangement, newLockedSlots)
                    #print("Suggested: %s" % suggestedSlotArrangement)
                    if len(vehiclesToAllocate) == 2:
                        #print("BIG ERROR")
                        newSlotArrangement = suggestedSlotArrangement
                        suggestedSlotArrangement, suggestedCost = self.allocateSlots(vehiclesToAllocate[1], newSlotArrangement, newLockedSlots)
                    if suggestedSlotArrangement is not None:
                        if cost > suggestedCost + suggestedSlot - firstFeasibleSlot:
                            slotAllocated = True
                            slotsToReturn = suggestedSlotArrangement
                            cost = suggestedCost + suggestedSlot - firstFeasibleSlot
                            #print("New best arrangement: %s for placing %s" % (slotsToReturn, vehiclesToAllocate[0]))
                    else:
                        pass
                else:
                    #print("Not feasible or is locked")
                    pass
                suggestedSlot += 1
                if suggestedSlot >= params.NUMBER_OF_SLOTS:
                    break
            else:
                #print("Available Slot Found: %s" % suggestedSlot)
                if cost > suggestedSlot - firstFeasibleSlot:
                    #print("Best alt")
                    slotsToReturn = copy.deepcopy(slots)
                    slotsToReturn[suggestedSlot].append(newVehicle)
                    cost = suggestedSlot - firstFeasibleSlot
                    slotAllocated = True
        if slotAllocated is not False:
            #print("Returning: %s" % slotsToReturn)
            return slotsToReturn, cost
        else:
            #print("Returning None")
            return None, None

    def assignArrivalTimesToSlots(self, timeNow):
        for i, slot in enumerate(self.slots):
            arrivalTimeToAssign = timeNow + (i + 1) * params.SLOT_SIZE
            for vehicle in slot:
                vehicle.assignedArrivalTime = arrivalTimeToAssign

def isSlotLocked(lockedSlots, suggestedSlot):
    if suggestedSlot in lockedSlots:
        return True
    else:
        return False

def existsConflictInFront(slots, slotIndex, vehicleToAllocate, lockedSlots):
    for i in range(0, slotIndex):
        for vehicle in slots[i]:
            #print("Foo")
            if vehicle.source == vehicleToAllocate.source:
                if vehicle.detectionTime > vehicleToAllocate.detectionTime and i in lockedSlots:
                    return True
    return False

def existsConflictBehind(slots, slotIndex, vehicleToAllocate, lockedSlots):
    for i in range(slotIndex + 1, len(slots)):
        for vehicle in slots[i]:
            #print("Baz")
            if vehicle.source == vehicleToAllocate.source:
                if vehicle.detectionTime < vehicleToAllocate.detectionTime and i in lockedSlots:
                    return True
    return False

def isSlotFeasible(slots, slotIndex, vehicleToAllocate, lockedSlots):
    if existsConflictInFront(slots, slotIndex, vehicleToAllocate, lockedSlots) or existsConflictBehind(slots, slotIndex, vehicleToAllocate, lockedSlots):
        return False
    else:
        return True

def isSlotAvailable(slots, slotIndex, vehicle, lockedSlots):
    #print("Checking slot %s", slotIndex)
    #print(slots)
    if slots[slotIndex] == []:
        if isSlotFeasible(slots, slotIndex, vehicle, lockedSlots):
            return True
    elif len(slots[slotIndex]) == 1 and isDoubleVehicleCompatible(slots[slotIndex][0], vehicle):
        if isSlotFeasible(slots, slotIndex, vehicle, lockedSlots):
            return True
    return False

def isDoubleVehicleCompatible(v1, v2):
    if v1.source == v2.destination and v1.destination == v2.source:
        return True
    elif (v1.source + 1) % 4 == v1.destination:
        # right turn v1
        if v2.source == v1.destination and (v2.source + 2) % 4 == v2.destination:  # v2 straight from v1 dest
            return True
        elif v2.destination == v1.source and (v2.source + 2) % 4 == v2.destination:  # v2 straight to v1 source
            return True
        elif v2.source != v1.destination and v2.source != v1.source and v2.destination != v1.destination and v2.destination != v1.source:
            return True
        elif v2.destination == v1.source and (v2.source + 1) % 4 == v2.destination:
            return True
    elif (v2.source + 1) % 4 == v2.destination:
        # right turn v2
        if v1.source == v2.destination and (v1.source + 2) % 4 == v1.destination:  # v1 straight from v2 dest
            return True
        elif v1.destination == v2.source and (v1.source + 2) % 4 == v1.destination:  # v1 straight to v2 source
            return True
        elif v1.source != v2.destination and v1.source != v2.source and v1.destination != v2.destination and v1.destination != v2.source:
            return True
        elif v1.destination == v2.source and (v1.source + 1) % 4 == v1.destination:
            return True

if __name__ == "__main__":
    main()
