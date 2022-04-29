from simulation import Simulation
from time import time
from event_templates import housing, alloys, electronics, food, timber, manufacturing, \
    tornado, earth_quake, fire, tsunami, space_exploration, buried_treasure, nuclear_fusion, universal_recycling
from globals import DEPTH_BOUND, FRONTIER_MAX_SIZE, MY_COUNTRY, GAMMA, C,  K, X_0, SHORT_OUTPUT


def main():
    run_simulation(input_country_file="inputs/input_countries.xlsx",
                   input_resource_file="inputs/input_resources.xlsx",
                   output_filename="outputs/output_schedule.txt",
                   output_count=10)


def run_simulation(input_country_file: str, input_resource_file: str, output_filename: str, output_count: int) -> None:
    game_simulation = Simulation(transform_templates=[housing, alloys, electronics, food, timber, manufacturing],
                                 random_events_list=[tornado, earth_quake, fire, tsunami, space_exploration, buried_treasure, nuclear_fusion, universal_recycling],
                                 initial_states_file=input_country_file,
                                 resource_input_filename=input_resource_file)
    start_time = time()
    print("Searching...\n")
    result_priority_queue = game_simulation.generate_schedules(DEPTH_BOUND, FRONTIER_MAX_SIZE)
    time_elapsed = time() - start_time

    important_variables = [("Centric Country:", MY_COUNTRY), ("Resource Input File:", input_resource_file),
                           ("Country Input File:", input_country_file), ("Output File:", output_filename),
                           ("Output Count:", output_count), ("Depth Bound:", DEPTH_BOUND),
                           ("Frontier Size:", FRONTIER_MAX_SIZE), ("Gamma:", GAMMA), ("C:", C), ("k:", K),
                           ("x_0:", X_0)]

    output_string = "\n==========================================================================\n"
    output_string += 'Important Variables:\n--------------------\n'
    for variable in important_variables:
        output_string += str(variable[0]) + " " + str(variable[1]) + "\n"
    output_string += "==========================================================================\n"
    output_string += ("Execution Time (s): " + str(round(time_elapsed, 3)) + "\n")
    output_string += "==========================================================================\n"
    try:
        for i in range(0, output_count):
            if SHORT_OUTPUT:
                current_result = result_priority_queue.get()
                current_schedule = current_result.partial_schedule
                world_state = current_schedule[len(current_schedule) - 1]
                current_state_expected_utility = world_state[1]
                output_string += "EU: " + str(round(current_state_expected_utility, 4)) + "\n"
            else:
                output_string += "\nSchedule #" + str(i + 1) + ": \n"
                current_result = result_priority_queue.get()
                current_schedule = current_result.partial_schedule
                for world_state in current_schedule:
                    current_state = world_state[0]
                    current_state_expected_utility = world_state[1]
                    output_string += str(current_state) + " EU: " + str(round(current_state_expected_utility, 4)) + "\n"
        print(output_string)
        # write_output(output_filename, output_string)
    except:
        print("ERROR: Not enough output schedules generated. Adjust global variables and try again")


def write_output(output_file: str, output_string: str) -> None:
    output_file = open(output_file, "w")
    output_file.write(output_string)
    output_file.close()


if __name__ == "__main__":
    main()
