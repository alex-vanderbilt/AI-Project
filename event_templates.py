from models import Transform, RandomEvent

# Represents the Housing transform with some of my own changes
housing = Transform(transform_name="Housing",
                    input_resources={"R1": 5, "R2": 1, "R3": 5, "R4": 3, "R21": 1},
                    output_resources={"R1": 5, "R4": 2, "R23": 1, "R23'": 1})

# Represents the Alloys transform with some of my own changes
alloys = Transform(transform_name="Alloys",
                   input_resources={"R1": 1, "R2": 2, "R4": 3},
                   output_resources={"R1": 1, "R4": 2, "R21": 2, "R21'": 2})

# Represents the Electronics transform with some of my own changes
electronics = Transform(transform_name="Electronics",
                        input_resources={"R1": 1, "R2": 3, "R4": 3, "R21": 2},
                        output_resources={"R1": 1, "R4": 2, "R22": 2, "R22'": 1})

# This is a new transform added. covered in the project presentation
food = Transform(transform_name="Food",
                 input_resources={"R1": 2, "R3": 2, "R4": 3, "R5": 3},
                 output_resources={"R1": 2, "R4": 1, "R5": 2, "R24": 3, "R24'": 1})

# This is a new transform added. covered in the project presentation
timber = Transform(transform_name="Timber",
                   input_resources={"R1": 2, "R4": 3, "R5": 3},
                   output_resources={"R1": 2, "R3": 10, "R4": 1, "R5": 2})

# This is a new transform added. covered in the project presentation
manufacturing = Transform(transform_name="Manufacturing",
                          input_resources={"R1": 100, "R3": 150, "R4": 100, "R5": 75, "R21": 20, "R22": 100},
                          output_resources={"R1": 90, "R4": 50, "R5": 65, "R25": 15, "R21'": 2, "R22'": 10, "R25'": 10})




# Newly added Random Events:
tornado = RandomEvent(random_event_name="Tornado Hit",
                      event_multiplier=0.5,
                      probability_of_success=0.1,
                      resources_effected_list=["R1", "R3", "R4", "R5", "R21", "R22"])