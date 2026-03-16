"""Constants for the city app."""

# Map size is fixed at 20x20 tiles
MAP_SIZE = 20

# Initial number of country buildings to place on map generation
INITIAL_COUNTRY_BUILDINGS = 3

# Wall hitpoints
WALL_DECAY_PER_ROUND = 10

# Siege system
SIEGE_ADVANCE_ROUNDS = 3
SIEGE_STRENGTH_MIN = 50
SIEGE_STRENGTH_MAX = 300
SIEGE_FUZZ_MIN = 0.75
SIEGE_FUZZ_MAX = 1.25
SIEGE_FUZZ_ROUND_TO = 50
SIEGE_DAMAGED_THRESHOLD = 0.6
