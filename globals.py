# All global variables are described in depth in the README file

# State variables:
MY_COUNTRY = "Atlantis"
DEPTH_BOUND = 8
FRONTIER_MAX_SIZE = 40
GAMMA = .95
C = -.01
K = 1
X_0 = 0

TRANSFERABLE_RESOURCES = ['R2', 'R3', "R4", 'R21', 'R22', 'R23', "R24", "R25"]
# Acceptable values: Reserved, Moderate, Aggressive
PLAY_STYLE = "Aggressive"

# Transform Variables
MINIMIZE_MULTIPLIER = True
MINIMIZATION_FACTOR = 10

# Debug Variable
PRINT_WHILE_SEARCHING = False
SHORT_OUTPUT = False

# Country Resource Threshold goal:
RESOURCE_THRESHOLD = {'R2': 500, 'R3': 600, 'R4': 400, 'R5': 400}
UNDER_UTILIZATION_THRESHOLD = 0.8
OVERCONSUMPTION_THRESHOLD = 2

