ANIMATION_ON = False
ANIMATION_DISTANCE_SCALING = 1  # Scales travel distances from ROAD_LENGTHS for nicer animation

TIME_MAX = 3600  # Simulation length
NUMBER_OF_ROADS = 4  # Roads connecting at intersection
TURN_PROBABILITIES = [[0.33, 0.33, 0.34], [0.33, 0.33, 0.34], [0.33, 0.33, 0.34], [0.33, 0.33, 0.34]]  # Probabilities to turn to other roads based on origin
MEAN_INTER_ARRIVAL_TIMES = [12, 12, 12, 12]  # Mean inter arrival time of car from source road. Exponential Distribution.
CROSSING_CONNECTIONS = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]  # Possible turns from each road
ROAD_LENGTHS = [200, 200, 200, 200]  # Length of source road in m
SPEED_LIMIT = 14  # Max speed allowed in m/s
ARRIVAL_SPEED = 12  # Speed of vehicle at detectio in m/s
RESOLUTION = 1  # Time resolution of simulation, may not be needed.
 
SLOT_SIZE = 2  # Size of time slot for intersection in seconds
NUMBER_OF_SLOTS = 15  # ceil(ROAD_LENGTHS[0] / (SPEED_LIMIT / 4))   # Number of slots used for optimization
INTER_CAR_SPACE = 5  # Space between cars (front to front) in m
