from globals import GAMMA, MY_COUNTRY, C, K, X_0, IMPORT_PERCENT, EXPORT_PERCENT, MINIMIZE_MULTIPLIER,\
    MINIMIZATION_FACTOR, TRANSFERABLE_RESOURCES, PRINT_WHILE_SEARCHING, RESOURCE_THRESHOLD, \
    UNDER_UTILIZATION_THRESHOLD, OVERCONSUMPTION_THRESHOLD
from models import Transfer, Transform, Schedule, Country, ResourceWeight

import pandas as pd
import numpy as np
from queue import PriorityQueue
from copy import deepcopy


# The Simulation class is used to implement the forward, depth-first, heuristic based searching algorithm
# It is responsible for loading in input Country and Resource data as well as generating all potential schedules and
# sorting them based on expected utility which it calculates.
class Simulation:
    transform_templates: list
    initial_states_file: str
    resource_input_filename: str
    country_list: list
    resource_weight_list: list
    result_list: PriorityQueue
    visited_scheduled: list

    # When initializing a Simulation object we immediately load the input Country and Resource information
    def __init__(self, transform_templates: list, initial_states_file: str, resource_input_filename: str) -> None:
        self.transform_templates = transform_templates
        self.initial_states_file = initial_states_file
        self.resource_input_filename = resource_input_filename
        self.country_list = []
        self.result_list = PriorityQueue()
        self.queue = PriorityQueue()
        self.load_country_data()
        self.resource_weight_list = []
        self.load_resource_weights()

    # Load country data is used to take an input excel file and read in the countries and their initial states
    def load_country_data(self) -> None:
        data_frame = pd.DataFrame(pd.read_excel(self.initial_states_file))
        input_states = data_frame.set_index("Country").T.to_dict('dict')
        for country_name in input_states:
            self.country_list.append(Country(name=country_name, resource_dict=input_states[country_name]))

    # Load resource data is used to take an input excel file and read in the initial resource weights and names
    def load_resource_weights(self) -> None:
        resources_dataframe = pd.DataFrame(pd.read_excel(self.resource_input_filename))
        input_resources = resources_dataframe.set_index("Resource").T.to_dict('dict')
        for resource_name in input_resources:
            self.resource_weight_list.append(ResourceWeight(name=resource_name,
                                                            resource_weight=input_resources[resource_name]["Weight"],
                                                            display_name=input_resources[resource_name]["Name"]))

    # Generate schedules is used as the searching algorithm for the heuristic based DFS
    # Depth bound and Frontier Max Size are defined in the globals.py file for easy changes to be made
    def generate_schedules(self, depth_bound: int, frontier_max_size: int) -> PriorityQueue:
        # We initialize our priority queue with an empty schedule as well as initialize our visited list as empty
        self.queue.put((0, Schedule(utility=0, country_list=self.country_list, partial_schedule=[])))
        visited_schedules = []

        # We will iterate through the priority queue until it is empty (as is common in DFS searching)
        while not self.queue.empty():
            # We pop from the queue and grab the current schedule, world state
            current_schedule = self.queue.get()[1]
            current_world_state, current_partial_schedule = current_schedule.country_list, current_schedule.partial_schedule
            # If our previously generated partial schedule has reached the appropriate depth we are searching for, we add it to our results queue
            if len(current_partial_schedule) >= depth_bound:
                self.result_list.put(current_schedule)
            # Otherwise we ensure it has not already been visited
            elif current_schedule not in visited_schedules:
                visited_schedules.append(current_schedule)
                # We now iterate over all potential successors generated using the current world state
                for child_state in self.generate_successors(current_world_state):
                    next_world_state, next_action = child_state[0], child_state[1]
                    current_depth = len(current_partial_schedule) + 1
                    # We calculate the EU of the state we are currently analyzing
                    expected_state_utility = self.expected_utility(current_world_state, next_world_state, current_depth, next_action)
                    if PRINT_WHILE_SEARCHING:
                        print(next_action.to_string(self.resource_weight_list) + " EU: " + str(expected_state_utility))
                    next_partial_schedule = current_partial_schedule + [[next_action.to_string(self.resource_weight_list), expected_state_utility]]
                    child_schedule = Schedule(-1 * expected_state_utility, next_world_state, deepcopy(next_partial_schedule))
                    # We ensure that the child schedule has not already been visited and add it to the queue
                    if child_schedule not in visited_schedules:
                        self.queue.put((expected_state_utility, child_schedule))
                    # To ensure we stay within the gloablly defined frontier size, we will remove any excess states from the queue
                    while self.queue.qsize() > frontier_max_size:
                        self.queue.get()
        # Return the list of results generated
        return self.result_list

    # Generating all successor states given the current state of the world which include transforms and transfers
    def generate_successors(self, current_world_state: list) -> list:
        return self.generate_transforms(current_world_state) + self.generate_transfers(current_world_state)

    # Undiscounted Reward (AKA Reward) is defined as:
    #   R(c_i, s_j) = Q_end(c_i, s_j) – Q_start(c_i, s_j)
    # Or:
    #   R(S) = Quality of End State (S) - Quality of Start State (S)
    def undiscounted_reward(self, start_quality: float, end_quality: float) -> float:
        return end_quality - start_quality

    # Discounted Reward is defined as:
    #   DR(c_i, s_j) = gamma^N * (Q_end(c_i, s_j) – Q_start(c_i, s_j)), where 0 <= gamma < 1
    # Or:
    #   DR(S) = (Gamma ^ N) * Un-Discounted Reward(S), where N = depth and 0 <= Gamma < 1
    def discounted_reward(self, start_quality: float, end_quality: float, depth: int) -> float:
        return (GAMMA ** depth) * self.undiscounted_reward(start_quality, end_quality)

    # Expected Utility is defined as:
    #   EU(c_i, s_j) = (P(s_j) * DR(c_i, s_j)) + ((1-P(s_j)) * C), where c_i = self
    # Or (a little easier to read):
    #   EU of State (S) = Probability (S) will succeed * Discounted Reward (S) + ((1 - Probability (S) will succeed) * C)
    def expected_utility(self, current_world_state: list, next_world_state: list, depth: int, action: tuple) -> float:
        my_country_current_state = next((country for country in current_world_state if country.name == MY_COUNTRY), None)
        start_quality = self.state_quality(my_country_current_state)
        my_country_next_state = next((country for country in next_world_state if country.name == MY_COUNTRY), None)
        end_quality = self.state_quality(my_country_next_state)
        discounted_reward = self.discounted_reward(start_quality, end_quality, depth)
        success_probability = self.success_probability(current_world_state, next_world_state, depth, action)
        return 100 * (success_probability * discounted_reward + ((1 - success_probability) * C))

    # State Quality is defined as:
    #   SQ = (Resources available * Resource Weights) / Population
    # If we find that resources dip below 0 we negatively impact the state score
    def state_quality(self, input_country: Country) -> float:
        country_resources = input_country.resources
        negative_resources_found = False
        overconsumption_found = False
        under_resource_threshold = False
        state_quality = 0.0
        for current_resource in country_resources.keys():
            resource_quantity = country_resources[current_resource]
            resource_weight = next((resource for resource in self.resource_weight_list if resource.name == current_resource), None).resource_weight
            # Checking resource threshold
            if current_resource in RESOURCE_THRESHOLD:
                current_resource_threshold = RESOURCE_THRESHOLD[current_resource] * UNDER_UTILIZATION_THRESHOLD
                overconsumption_threshold = RESOURCE_THRESHOLD[current_resource] * OVERCONSUMPTION_THRESHOLD
                if resource_quantity - current_resource_threshold < 0:
                    under_resource_threshold = True
                if resource_quantity - overconsumption_threshold > 0:
                    overconsumption_found = True
            state_quality += (resource_quantity * resource_weight)
            if resource_quantity < 0: negative_resources_found = True
        normalized_quality = state_quality / country_resources["R1"]
        if under_resource_threshold: normalized_quality *= 0.8
        elif overconsumption_found: normalized_quality *= 0.5
        return normalized_quality - 1000 if negative_resources_found else normalized_quality

    # The probabilty a given state will succeed is different depending on whether we are performing a Transform or Transfer
    def success_probability(self, current_world_state: list, next_world_state: list, depth: int, type_of_action: tuple) -> float:
        if isinstance(type_of_action, Transfer):
            return self.transfer_success_probability(current_world_state, next_world_state, depth, type_of_action)
        if isinstance(type_of_action, Transform):
            return self.transform_success_probability(depth)

    # Transforms are generated using the input list of transform templates
    def generate_transforms(self, current_world_state: list) -> list:
        transform_list = []
        for transform in self.transform_templates:
            transform_execution = transform.execute(current_world_state)
            if transform.transform_multiplier != 0:
                transform_list.append([transform_execution, transform])
            # To maximize our potential options, if MINIMIZE_MULTIPLIER is set we will generate a second set of Transforms
            if transform.transform_multiplier > 10 and MINIMIZE_MULTIPLIER:
                transform_execution = transform.execute_given_multiplier(current_world_state, transform.transform_multiplier / MINIMIZATION_FACTOR)
                transform_list.append([transform_execution, transform])
        return transform_list

    # Transfers are generated as both import to and export from every country while always involving our represented country
    def generate_transfers(self, current_world_state: list) -> list:
        transfers = []
        my_country = next((country for country in current_world_state if country.name == MY_COUNTRY), None)
        for country in current_world_state:
            for resource in TRANSFERABLE_RESOURCES:
                if country is not my_country:
                    # We base our generated transfers on the IMPORT and EXPORT percents, defined in globals.py
                    if country.resources[resource] > 0:
                        import_transfer = Transfer(current_world_state, country.name, MY_COUNTRY, (resource, IMPORT_PERCENT * country.resources[resource]))
                        transfers.append([import_transfer.execute(), import_transfer])
                    if my_country.resources[resource] > 0:
                        export_transfer = Transfer(current_world_state, MY_COUNTRY, country.name, (resource, EXPORT_PERCENT * my_country.resources[resource]))
                        transfers.append([export_transfer.execute(), export_transfer])

        return transfers

    # Transfer success probability is used to calculate the probability a country will participate in a given schedule
    # Currently transfers are restricted to only involve two countries, one of which we are being represented by
    # The success probability is computed using the logistic function as:
    # Prob Success for an individual country = Logistic Function(L, k, x_0, x = Discounted Reward of that country)
    # We calculate the overall probability of success as the product of both participating countries success probabilities
    def transfer_success_probability(self, current_world_state: list, next_world_state: list, depth: int, transfer: Transfer) -> float:
        if transfer.export_country == MY_COUNTRY:
            transfer_country = transfer.import_country
        else:
            transfer_country = transfer.export_country

        start_state_quality_other_country = self.state_quality(transfer_country)
        end_state_quality_other_country = self.state_quality(transfer_country)
        other_county_discounted_reward = self.discounted_reward(start_state_quality_other_country, end_state_quality_other_country, depth)

        my_country = next((country for country in next_world_state if country.name == MY_COUNTRY), None)
        end_state_quality_my_country = self.state_quality(my_country)
        my_country = next((country for country in current_world_state if country.name == MY_COUNTRY), None)
        start_state_quality_my_country = self.state_quality(my_country)
        my_county_discounted_reward = self.discounted_reward(start_state_quality_my_country, end_state_quality_my_country, depth)

        other_country_success_probability = self.logistic_function(L=1, x=other_county_discounted_reward)
        my_country_success_probability = self.logistic_function(L=1, x=my_county_discounted_reward)
        success_probability = other_country_success_probability * my_country_success_probability
        if success_probability == 0:
            raise RuntimeError
        else:
            return success_probability

    # Used to calculate the probability of success of a given transform based on current depth of the search
    # The deeper the search, the lower the likely hood the transform will be able to take place given the ambiguity of schedules
    def transform_success_probability(self, depth: int) -> float:
        return .9 ** depth

    # Logistic Function as defined here: https://en.wikipedia.org/wiki/Logistic_function
    # This is used for determining the probability of success
    def logistic_function(self, L: float, x: float) -> float:
        return L / (1 + np.exp(-K * (x - X_0)))